from MadeDataSet.BasicParameters import BasicParameters
from MadeDataSet.CreateDirectory import CreateDirectory
from MadeDataSet.DivisionOnImgFragment import DivisionOnImgFragment



if __name__ == '__main__':
    name_folder_dataset = BasicParameters.NAME_FOLDER_DATASET
    name_folder_img = f'{name_folder_dataset}/{BasicParameters.NAME_FOLDER_IMG}'
    name_folder_masks = f'{name_folder_dataset}/{BasicParameters.NAME_FOLDER_MASKS}'
    name_folder_json = f'{name_folder_dataset}/{BasicParameters.NAME_FOLDER_JSONS}'

    crtdir = CreateDirectory()
    crtdir.CheckCreareDirectory(name_folder_dataset)
    crtdir.CheckCreareDirectory(name_folder_img)
    crtdir.CheckCreareDirectory(name_folder_masks)
    crtdir.CheckCreareDirectory(name_folder_json)

    coord = {'latLower': 56.225,
             'lonLower': 50.8804,
             'latHigher': 58.902,
             'lonHigher': 55.0607}

    division = DivisionOnImgFragment(coord)
    division.Start(name_folder_img, name_folder_masks, name_folder_json)

