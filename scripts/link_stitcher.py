import urllib.parse
import re

# Configuration
notebook_url = "https://github.com/org/repo/blob/branch/notebooks/example.ipynb"
permalink = ""  # Permalink copied from GeoLab Server Launch Configuration
jupyterhub_url = "https://geolab.earthscope.cloud"

# Extract repository information from notebook URL
git_repo_url = notebook_url.split("/blob/")[0]
branch = notebook_url.split("/blob/")[1].split("/")[0]
notebook_path = "/".join(notebook_url.split("/blob/")[1].split("/")[1:])
notebook_suburl = git_repo_url.split("/")[-1] + "/" + notebook_path

# Build git-pull URL (requires nbgitpuller)
gitpull_next = (
    f"/hub/user-redirect/git-pull"
    f"?repo={git_repo_url}"
    f"&branch={branch}"
    f"&urlpath=lab/tree/{notebook_suburl}"
)

# Build spawn URL with git-pull as next parameter
spawn_next = "/hub/spawn?next=" + urllib.parse.quote(gitpull_next, safe="")

# Extract fancy-forms-config from permalink and enable auto-start
config_match = re.search(r"%23.+?(?=%7D)", permalink)
if config_match:
    fancy_forms_config = config_match[0].replace(
        "%22autoStart%22%3A%22false%22",
        "%22autoStart%22%3A%22true%22"
    )
    # Construct final URL
    final_url = (
        f"{jupyterhub_url}/hub/login"
        f"?next={urllib.parse.quote(spawn_next, safe='')}"
        f"{fancy_forms_config}%7D"
    )
    print(final_url)
else:
    print("Error: Could not extract config from permalink")