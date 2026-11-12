# Notebook Guidelines
Contributions should help another researcher understand, run, and adapt a geophysical workflow in GeoLab. The guidelines below focus on clear documentation, reproducibility, and reuse. Notebooks do not need to be complete tutorials. 

## Contents
1. Notebooks should focus on a geophysical workflow or analysis technique and use data from the NSF National Geophysical Facility Archive.
2. Begin each notebook with a short introduction describing:
    - What the notebook does and why the workflow is useful
    - What outputs or results users can expect
    - Any assumed background, required data access, or setup instructions
    - Any notebooks or steps that must be completed first
3. Make inputs that users are likely to change, such as network, station, time range, or processing parameters, easy to find and modify. Explain any data requirements or assumptions that limit where the workflow can be applied.
4. A README file is strongly encouraged, especially for projects containing multiple files or notebooks. Use it to explain where to begin and provide shared setup instructions.

## Running in GeoLab
1. Test each notebook in GeoLab by restarting the kernel and running all cells in order. For notebook sequences, test the complete sequence in its intended order.
2. Document the GeoLab environment or image used, any additional dependencies and installation steps, and any required server size. Include the date last tested. Shared setup information may be provided in the README and linked from each notebook.
3. Provide working instructions for accessing required data and supporting files. Avoid paths specific to your own account, and do not include passwords, tokens, or other credentials.
4. Flag steps that require substantial runtime, memory, storage, or downloads so users can plan accordingly.

## Formatting and Readability
1. Use Markdown headings to organize the notebook into logical workflow stages.
2. Include enough explanatory text and code comments for a researcher unfamiliar with the workflow to follow the major steps. Explain important assumptions and processing choices.
3. Describe what successful execution should produce at key steps, such as a plot, output file, or data product. Provide enough context for users to interpret the results.
4. Label plots with meaningful titles, axes, and units where applicable.
5. If multiple notebooks must be run in a particular order, number the filenames and explain the sequence in the README or introductory notebook.
6. Link to relevant software or method documentation where it helps users understand or adapt the workflow.

## Maintenance
1. Specify a maintainer and contact information. Users who encounter problems with a notebook are encouraged to contact the maintainer or raise an issue in the project's repository. EarthScope is not responsible for keeping contributed code up to date or fixing bugs identified by the community.
2. Projects will be reviewed by EarthScope staff annually. Projects that no longer run properly will be flagged, and maintainers will be contacted. If the issues are not resolved, the project's library listing will be archived. 
