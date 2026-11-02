# Contributing to the library

The Community Library relies on contributions from researchers like you! 
If you've built something cool in GeoLab, we ask you to share it with the Geophysical Community. Adding your project to the library is as simple as adding a metadata listing `yml' file to our repository. 

Our library considers project submissions of the following types:
1. Notebooks: .ipynb files that run through a particular scientific workflow or analysis technique
2. Container Images: Installations of domain-specific software, packages, or key tools in a custom geolab image[link].  

Steps to submit a project:
1. Create your project and put in a github repository. Test it in GeoLab and ensure it meets our [Contribution Guidelines](add link). 
2. Make a local copy of the template.yml file from the root of this github repository. Rename it with your project name and fill in the metadata about your project. A few hints:
    - Include the URL to a thumbnail image representing your project or institution. We recommend adding the image file to your github repository and linking to the [raw github file](https://docs.github.com/en/repositories/working-with-files/using-files/viewing-and-understanding-files). A 16:9 aspect ratio in landscape orientation is recommended to prevent image cropping.
    - If submitting notebooks, create a [nbgitpuller link](https://docs.earthscope.org/geolab/advanced_topics/nbgitpuller.md) to your repository.
    - If submitting a container image, create a [permalink](https://2i2c.org/jupyterhub-fancy-profiles/v0.7.0/permalink/) to the GeoLab launch page with your image tag populated.
    - Template fields are customizable. If there is a `key: value` pair that is important for your project that is not already in the template, you can add it to the file for your project. It will be displayed in the long-form pop-out when your project is clicked on in the library.   


3. Make a pull request in our github repository to add your template.yml file to the `/projects` directory. An admin will review your project and pull request, and contact you if any questions, clarifications, or fixes need to be addressed.
4. That's it! Once your PR is merged, your project will be available on the Project Listing page for other community users. 
5. Make a post on our [community forum](https://earthscope.discourse.group/) to share your work! 