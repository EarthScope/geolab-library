# Image Guidelines

If you wish to contribute Software Container Images to the GeoLab Community Library, we ask that they meet certain standards for reproducibility and usability. 

## Functionality
1. The container image runs in GeoLab.
2. The container image includes Geophysics-related software that might be of use to researchers processing NSF National Geophysical Facility Data.

## Reproducibility
1. The dockerfile and/or configuration files used to build the image must be shared in a public git repository. The repo URL must be included in the template.yml
2. The image is stored in a public container registry, i.e., dockerhub, ghcr, or ecr. The image tag must be provided in the template.yml file. 

    Recommended: Your image tag id should contain a descriptive name and version number. 


## Security
1. 