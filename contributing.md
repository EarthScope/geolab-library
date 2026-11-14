# Contributing to the Library

The Community Library relies on contributions from researchers like you! 
If you've built something cool in GeoLab, we ask you to share it with the community. _Adding your project to the Library is as simple as adding a metadata listing .yml file to our repository_. 

Just like an online catalog at your local library, the GeoLab-Library listing _describes_ the material, but the content of the actual resource is the responsibility of the author, not the librarian (EarthScope). The Library is designed to make GeoLab-compatible materials that exist in github or gitlab more readily searchable and accessible to researchers -- but YOU, the author, maintain ownership and control over the content, as well as responsibility for keeping it updated. 


Our library considers project submissions of the following types:
1. __Notebooks__: `.ipynb` files that run through a particular scientific workflow or analysis technique
2. __Container Images__: Installations of domain-specific software, packages, or key tools in a [custom GeoLab image](https://docs.earthscope.org/geolab/advanced-topics/environments/building-custom-images).  

## Steps to submit a project:
1. __Create your project and put in a github or gitlab repository.__ Test it in GeoLab and ensure it meets our Contribution Guidelines for [Notebooks](notebook_guidelines.md) and/or [Container Images](image_guidelines.md).

2. __Make a local copy of the template.yml file,__ which is located at the root of the [geolab-library github repository](https://github.com/EarthScope/geolab-library/blob/main/template.yml). Rename the copy with your project name and fill in the metadata about your project. A few hints:

    - Generally speaking, you should provide one template listing per repository. We recommend pointing your nbgitpuller link (below) to the repository readme. However, there are cases where this might not be the best strategy, for example:
      - The repository contains multiple, distinct projects or notebook sets. For example, the [geolab-tutorials]() repository contains different notebook series for getting started with geodetic data, seismic data, and advanced topics like dask. Each folder directory in the repository has its own listing, as they cover different, unique topics. 
      - Your project might need more than one listing. For example, if you have both a software container image _and_ tutorial notebooks that demonstrate how to use the software, and those resources live in different github repositories. 
    Keep in mind that each template.yml file submitted will generate one tile (catalog listing) in the Library. The 'Open in Geolab' button on the tile will launch to your nbgitpuller link. 

    - Generating links:
      - If submitting a container image, create a [permalink](https://2i2c.org/jupyterhub-fancy-profiles/v0.7.0/permalink/) to the GeoLab launch page with your image tag populated.
      - If submitting notebooks that run in the default GeoLab environment, create a [nbgitpuller link](https://docs.earthscope.org/geolab/advanced-topics/nbgitpuller) to your repository. We recommend pointing at the README or first notebook in your series.
      - If your notebooks need to run in a different environment or require more than the default resource allocation, _make a note_ in the pull request comment field and we will help generate a custom link that combines the server parameters with the nbgitpuller link. 


    - Include the URL to a thumbnail image representing your project or institution. We recommend adding the image file to _your_ github repository and linking to the raw github file. A 16:9 aspect ratio in landscape orientation is recommended to prevent unwanted image cropping.

    - Template fields are customizable. If there is a `key: value` pair that is important for your project that is not already in the template, you can add it to the file for your project. It will be displayed in the long-form pop-out when someone clicks on your project in the Library. Likewise, if a field in the template doesn't make sense for your project, you can omit it. 

    - Add a handful of keyword tags to your project to improve searchability. Specific sub-domains, analysis techniques, data types, or key software packages are good choices. 


3. __Make a pull request (PR) in the [geolab-library github repository](https://github.com/EarthScope/geolab-library) to add your template.yml file to the `/projects` directory.__ An admin will review your project and pull request, and contact you if any questions, clarifications, or fixes need to be addressed.

4. That's it! Once your PR is merged, your project will be available on the [Project Directory](project_tiles.md) page for other community users.

5. __Make a post on our [community forum](https://earthscope.discourse.group/)__ to share your work! 
