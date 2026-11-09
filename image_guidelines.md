# Image Guidelines

If you wish to contribute Software Container Images to the GeoLab Community Library, we ask that they meet certain standards for reproducibility and usability.

## Functionality

1. The container image must run in GeoLab.
2. The container image includes Geophysics-related software that might be of use to researchers processing NSF National Geophysical Facility Data.

## Reproducibility

1. The Dockerfile and/or configuration files used to build the image must be shared in a public git repository. The repo URL must be included in the template.yml
2. The image is stored in a public container registry, i.e., Docker Hub, GitHub Container Registry, or Amazon ECR. The image tag must be provided in the template.yml file.

    Recommended: Your image tag id should contain a descriptive name and version number.

## Security

Container images bundle an operating system and hundreds of packages. New vulnerabilities are discovered and published at [CVE Program Mission](https://cve.org). The practices listed below are used to maintain and secure the [geolab-base](https://github.com/EarthScope/GeoLab/tree/main/geolab-base) image.

1. **Pin the base image.** Start `FROM` a specific tag, not `latest`, so builds are reproducible and you know which fixes the image includes. If you build on geolab-base, use its most recent release.
2. **Apply operating system security updates during the build.** A pinned base image only includes the fixes that existed when it was built. Run the package manager's upgrade as `root`, clean up, then switch to the notebook user:

    ```dockerfile
    USER root
    RUN apt-get update > /dev/null \
        && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y --no-install-recommends \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*
    USER ${NB_USER}
    ```

3. **Scan the image before you submit it.** Scan the built image with [Trivy](https://trivy.dev/) (or a similar scanner, such as Docker Scout or Grype) and fix every critical or high vulnerability that has a fix available:

    ```shell
    trivy image --severity HIGH,CRITICAL --ignore-unfixed username/my-geolab-image:0.1.0
    ```

    If Trivy isn't installed, you can run it in Docker:

    ```shell
    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
      aquasec/trivy:latest image --severity HIGH,CRITICAL --ignore-unfixed \
      username/my-geolab-image:0.1.0
    ```

    If you publish an image to Amazon ECR or Docker Hub, you can turn on the registry's scanning. ECR's basic scanning can run every time you push an image, and Docker Hub can analyze your repositories with Docker Scout.

    Rebuild and scan again until the remaining findings are ones with no fix available. Record changes in a CHANGELOG.

4. **Require fixed versions of vulnerable Python packages.** When a scan reports a vulnerable package, set a minimum version that includes the fix in `environment.yml` or `requirements.txt` (for example, `urllib3>=2.8.0`) rather than an exact pin. If no fixed version is available, the build fails instead of quietly keeping the old version.
5. **Do not include secrets.** Images must not contain credentials, tokens, SSH keys, or `.env` files. Pass them in when the container runs, never with `COPY` or `--build-arg`.
6. **Keep the image up to date.** Rebuild and scan the image regularly, and whenever the base image releases a new version. Publish each rebuild with a new tag, and list the security fixes in a CHANGELOG.