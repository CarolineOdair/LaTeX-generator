import regex
import os
import textwrap

def main():
    REPORT_FOLDER = "sprawozdanie"

    IMAGES_PATH = fr".\{REPORT_FOLDER}\images"
    TEMPLATE_FILE_PATH = r".\templates\sprawozdanie_template.tex"
    NEW_FILE_NAME = fr".\{REPORT_FOLDER}\sprawozdanie.tex"

    IMG_SIZE = {"width": 15.5, "height": None}

    generator = LatexGenerator(IMG_SIZE)
    doc = generator.generate(IMAGES_PATH, TEMPLATE_FILE_PATH)
    # print(doc)

    with open(NEW_FILE_NAME, "w", encoding="utf-8") as file:
        file.write(doc)



class LatexGenerator():
    def __init__(self, img_size:dict={}):

        self.img_size = img_size


    def generate(self, img_path:str, template_file_path:str):

        files = self.get_img_files(img_path)
        images = self.get_list_with_files(files)
        content = self.generate_content(images)
        document = self.get_finished_document(content, template_file_path)

        return document

    def get_img_files(self, path:str):
        images = self.get_all_valid_files(path)
        return images

    def get_all_valid_files(self, path:str):

        dir_list = os.listdir(path)

        img_list = []

        pattern = "^([^#]*##([0-9]+([.][0-9]+)?)[.]((png)|(jpg)|(jpeg)))$"
        for file in dir_list:
            required_path_part = regex.findall(pattern, file, flags=regex.I)
            if required_path_part:
                img_list.append(required_path_part[0][0])

        return img_list

    def get_list_with_files(self, img_list:list):

        files = []

        for img in img_list:

            sub, num, short_name = self. get_subsection_and_img_number_from_name(img)

            img_info = {"name": img,
                        "short_name": short_name,
                        "subsection": sub,
                        "img_num": num}

            files.append(img_info)

        return files

    def get_subsection_and_img_number_from_name(self, img:str):
        """ img name pattern:
        something#1.2.png   or  something#1.png     or  #1.png"""

        img_id = img.split("##")[-1]  # gets part after `#`
        short_name = img.split("##")[0]  # gets part before `#`

        id_parts = img_id.split(".")  # splits by `.`
        subsection = int(id_parts[0])  # gets subsection part
        if len(id_parts) > 2:  # img number is optional so gets img number if exists
            img_number = int(id_parts[1])
        else:
            img_number = None

        return subsection, img_number, short_name


    def generate_content(self, images:list):
        subsection_number = self.get_subsection_number(images)

        sub_content = []

        for subsection in range(1, subsection_number+1):
            sub_num = subsection
            sub_images = [img_dict for img_dict in images if img_dict["subsection"] == sub_num]

            sub_content.append(self.get_subsection_content(sub_images))

        # join subcontent with breaks between, it improves how latex renders
        content = "\n\n\\pagebreak\\quad\n".join(sub_content)
        self.content = content
        return content

    def get_subsection_content(self, images:list):

        subsection_content = f"\n\\subsection{{{images[0]['short_name'] if 0<len(images) else 'None'}}}\n"

        if images:
            images = sorted(images, key=lambda x: (x["img_num"] is None, x["img_num"]))  # handles None values

            figures = [self.generate_figure(img) for img in images]
            subsection_content += "".join(figures)

        return subsection_content

    def generate_figure(self, image:dict) -> str:

        # `size_arguments` is a string containing img size values to insert into latex code
        # takes dict with `width` and/or `height` keys
        size_arguments = ",".join([f"{param}={val}cm" for param, val in self.img_size.items() if val is not None])

        # textwrap.dedent needed to remove unwanted indents from str
        template = r"""
            \begin{figure}[!htb]
                \centering
                \includegraphics[<size_argument>]{<name>}
                \caption{}
                \label{fig:<subsection>.<img_num>}
            \end{figure}"""
        template = textwrap.dedent(template)

        template = template.replace("<size_argument>", size_arguments)
        template = template.replace("<name>", image["name"])
        template = template.replace("<subsection>", str(image["subsection"]))
        figure = template.replace("<img_num>", str(image["img_num"]))

        return figure

    def get_subsection_number(self, images:list):
        return max([img["subsection"] for img in images])

    def get_finished_document(self, content:str, template_file_path:str):

        with open(template_file_path, encoding="utf-8") as file:
            document = file.read()

        document = document.replace("<CONTENT>", content)
        return document



if __name__ == "__main__":
    main()
