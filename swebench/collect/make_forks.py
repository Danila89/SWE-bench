import requests
import os

# GitHub API endpoint
API_URL = "https://api.github.com"

# Replace with your GitHub Personal Access Token
TOKEN = os.environ.get("GITHUB_TOKEN")

# Replace with your organization name
ORG_NAME = "mirror-dump"

# List of repositories to fork (format: "owner/repo")
REPOS_TO_FORK = ['django/django',
 'Qiskit/qiskit',
 'jupyterlab/jupyterlab',
 'googleapis/google-cloud-python',
 'open-mmlab/mmdetection',
 'scikit-learn/scikit-learn',
 'kubeflow/pipelines',
 'psf/requests',
 'sympy/sympy',
 'conda/conda',
 'pydicom/pydicom',
 'wagtail/wagtail',
 'JohnSnowLabs/spark-nlp',
 'ytdl-org/youtube-dl',
 'tiangolo/fastapi',
 'docker/compose',
 'pallets/flask',
 'mwaskom/seaborn',
 'apache/airflow',
 'sqlfluff/sqlfluff',
 'mesonbuild/meson',
 'ray-project/ray',
 'matplotlib/matplotlib',
 'DataDog/integrations-core',
 'pantsbuild/pants',
 'tensorflow/models',
 'pylint-dev/pylint',
 'scipy/scipy',
 'pyvista/pyvista',
 'numpy/numpy',
 'sphinx-doc/sphinx',
 'google/jax',
 'marshmallow-code/marshmallow',
 'ipython/ipython',
 'dagster-io/dagster',
 'pypa/pip',
 'celery/celery',
 'python/typeshed',
 'pytest-dev/pytest',
 'pylint-dev/astroid',
 'pydata/xarray',
 'PrefectHQ/prefect',
 'pvlib/pvlib-python',
 'apache/mxnet',
 'huggingface/transformers',
 'conan-io/conan',
 'astropy/astropy',
 'twisted/twisted',
 'Lightning-AI/lightning',
 'gitpython-developers/GitPython',
 'pandas-dev/pandas',
 'pyca/cryptography',
 'explosion/spaCy']

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def fork_repository(repo):
    owner, repo_name = repo.split("/")
    url = f"{API_URL}/repos/{owner}/{repo_name}/forks"
    data = {"organization": ORG_NAME}
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 202:
        print(f"Successfully forked {repo} to {ORG_NAME}")
    else:
        print(f"Failed to fork {repo}. Status code: {response.status_code}")
        print(f"Error message: {response.json().get('message', 'No error message')}")

def main():
    for repo in REPOS_TO_FORK:
        fork_repository(repo)

if __name__ == "__main__":
    main()