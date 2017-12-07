import csv
import os


# In order for this to work, do the following:
#	- Create a folder for OpenImage data and put this script inside it (e.g. "OpenImage")
#	- Put the "annotated-images" folder and "images" folder in the OpenImage folder
#		- annotated-images contains image IDs, labels, and confidence intervals
#		- "images" contains images IDs and their URLs


def main():
    for folder in ["train", "validation", "test"]:
        images_file = open("./images/"+folder+"/images.csv", 'r')
        annots_file = open("./annotated-images/"+folder+"/annotations-human.csv", 'r')

        images_csv = csv.reader(images_file)
        annots_csv = csv.reader(annots_file)

        # Skip headers
        next(images_csv, None)
        next(images_csv, None)

        images_dict = {}
        for row in images_csv:
            #print(row)
            images_dict.update({row[0]:row[2]})

        annots_dict = {}
        for row in annots_csv:
            if row[3] != "1":
                continue

            # if row[0] in annots_dict:
            #     annots_dict[row[0]].append(row[2])
            # else:
            #     annots_dict[row[0]] = [row[2]]

            if row[0] in annots_dict:
                annots_dict[row[0]] += ("|"+row[2])
            else:
                annots_dict[row[0]] = row[2]

        if not os.path.exists("./compiled-images/" + folder):
            os.makedirs("./compiled-images/" + folder)

        with open("./compiled-images/" + folder + "/compiled.csv", "w") as writefile:
            for key in annots_dict:
                try:
                    writefile.write(key + "," + images_dict[key] + "," + annots_dict[key] + "\n")
                except:
                    continue

        writefile.close()


if __name__ == "__main__":
    main()
