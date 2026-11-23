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

    - Generally speaking, you should provide one template listing per repository. We recommend pointing your launch_link (below) to the repository readme. However, there are cases where this might not be the best strategy, for example:
      - The repository contains multiple, distinct projects or notebook sets. For example, the [geolab-tutorials](https://github.com/EarthScope/geolab-tutorials) repository contains different notebook series for getting started with geodetic data, seismic data, and advanced topics like dask. Each folder directory in the repository has its own listing, as they cover different, unique topics. 
      - Your project might need more than one listing. For example, if you have both a software container image _and_ tutorial notebooks that demonstrate how to use the software, and those resources live in different github repositories. 
    Keep in mind that each template.yml file submitted will generate one tile (catalog listing) in the Library. The 'Open in Geolab' button on the tile will launch to your launch_link. 

    - Generating a Launch Link:
      - If submitting a container image, create a [permalink](https://2i2c.org/jupyterhub-fancy-profiles/v0.7.0/permalink/). To do this, open the GeoLab server launch page, select your environment (custom image tag) and resource allocation, then click 'Permalink' on the upper right. This will copy the launch page configuration link to your clipboard.
      - If submitting notebooks that run in the default GeoLab environment, create a [nbgitpuller link](https://docs.earthscope.org/geolab/advanced-topics/nbgitpuller) to your repository and use it as your launch_link. We recommend pointing at the README or first notebook in your series. Note that to use `nbgitpuller` in custom Containter Images, `nbgitpuller` must be installed in the image. 
      - If you need *both* a custom environment or resource configuration, _and_ need to pull notebooks in from github, use the [`link_stitcher.py` script](https://github.com/EarthScope/geolab-library/blob/main/scripts/link_stitcher.py)to generate a hybrid `launch_link`. 


    - Include the URL to a thumbnail image representing your project or institution. We recommend adding the image file to _your_ github repository and linking to it. Either the file's GitHub page or its raw link works. The Library shows your whole image on a white background, so an image that isn't 16:9 (landscape) gets white bars beside or above it. A 16:9 image fills the card with no bars. [`scripts/thumbnailer.py`](https://github.com/EarthScope/geolab-library/blob/main/scripts/thumbnailer.py) resizes an image to 16:9 for you; see [Make a thumbnail](https://github.com/EarthScope/geolab-library#make-a-thumbnail) in the README. To have an image fill the space without resizing it, add `thumbnail_fit: crop`; its edges are then trimmed, which suits photos.

    - Template fields are customizable. If there is a `key: value` pair that is important for your project that is not already in the template, you can add it to the file for your project. It will be displayed in the long-form pop-out when someone clicks on your project in the Library. Likewise, if a field in the template doesn't make sense for your project, you can omit it. 

    - The `description` field supports basic Markdown: `#` headings, numbered and bulleted lists, ```` ``` ```` code blocks, `` `code` ``, `**bold**` and `[links](https://example.org)`. Start the field with `description: |` so line breaks are kept. Other Markdown, including HTML, is shown as plain text.

    - Add a handful of keyword tags to your project to improve searchability. Specific sub-domains, analysis techniques, data types, or key software packages are good choices. 


3. __Make a pull request (PR) in the [geolab-library github repository](https://github.com/EarthScope/geolab-library) to add your template.yml file to the `/projects` directory.__ An admin will review your project and pull request, and contact you if any questions, clarifications, or fixes need to be addressed.

4. That's it! Once your PR is merged, your project will be available on the [Project Directory](projects.md) page for other community users.

5. __Make a post on our [community forum](https://earthscope.discourse.group/)__ to share your work! 
