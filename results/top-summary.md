# wheelproof scan summary — top.jsonl

- packages scanned: 299 (1 errors/skips)
- **high severity: 45** (15%) — sdist build breaks under the 2026 removals
- at risk incl. medium: 96 (32%) — medium = uses removed APIs (pkg_resources/distutils) or legacy build path

## findings by type

| finding | count |
|---|---|
| no-pyproject | 44 |
| distutils | 38 |
| no-build-system | 21 |
| pkg-resources | 12 |
| tests-require | 9 |
| setup-requires | 6 |
| test-command | 1 |
| setup-cfg-deprecated-keys | 1 |

## at-risk packages

- **asgiref** 3.11.1: no-pyproject
- **asn1crypto** 1.5.1: no-pyproject
- **awscli** 1.45.26: no-build-system
- **azure-storage-blob** 12.30.0: no-build-system
- **babel** 2.18.0: distutils, no-build-system, pkg-resources
- **boto3** 1.43.26: no-build-system
- **botocore** 1.43.26: no-build-system
- **certifi** 2026.5.20: distutils
- **cffi** 2.0.0: distutils
- **cfgv** 3.5.0: no-pyproject
- **cython** 3.2.5: distutils, no-pyproject
- **datasets** 5.0.0: no-build-system
- **defusedxml** 0.7.1: distutils, no-build-system
- **deprecated** 1.3.1: no-build-system
- **dill** 0.4.1: distutils
- **distlib** 0.4.2: distutils
- **durationpy** 0.10: no-pyproject
- **email-validator** 2.3.0: no-build-system
- **et-xmlfile** 2.0.0: no-pyproject
- **fastjsonschema** 2.21.2: distutils, no-pyproject
- **fonttools** 4.63.0: distutils, no-build-system
- **frozenlist** 1.8.0: distutils
- **gitdb** 4.0.12: no-pyproject
- **google-analytics-admin** 0.30.0: no-pyproject
- **google-api-python-client** 2.197.0: no-pyproject
- **google-auth** 2.53.0: no-pyproject
- **google-auth-httplib2** 0.4.0: no-pyproject
- **google-auth-oauthlib** 1.4.0: no-pyproject
- **google-cloud-aiplatform** 1.157.0: no-pyproject
- **google-cloud-batch** 0.22.0: no-pyproject
- **google-cloud-compute** 1.48.0: no-pyproject
- **google-cloud-core** 2.6.0: no-pyproject
- **google-cloud-kms** 3.13.0: no-pyproject
- **google-cloud-secret-manager** 2.29.0: no-pyproject
- **google-cloud-storage** 3.11.0: no-pyproject
- **google-resumable-media** 2.10.0: no-pyproject
- **grpcio** 1.81.0: distutils
- **grpcio-tools** 1.81.0: distutils, pkg-resources
- **h11** 0.16.0: no-build-system
- **huggingface-hub** 1.18.0: no-build-system
- **identify** 2.6.19: no-pyproject
- **jedi** 0.20.0: no-build-system
- **jmespath** 1.1.0: no-pyproject
- **jsonpatch** 1.33: distutils, no-pyproject
- **jsonpointer** 3.1.1: no-pyproject
- **kubernetes** 36.0.2: no-pyproject
- **librt** 0.11.0: distutils
- **litellm** 1.88.1: pkg-resources
- **lxml** 6.1.1: distutils
- **more-itertools** 11.1.0: distutils
- **msal** 1.37.0: no-pyproject
- **msal-extensions** 1.3.1: no-pyproject
- **multiprocess** 0.70.19: distutils
- **mypy** 2.1.0: distutils
- **oauthlib** 3.3.1: no-pyproject
- **openpyxl** 3.1.5: no-pyproject
- **parso** 0.8.7: no-build-system
- **pexpect** 4.9.0: distutils, no-pyproject
- **pip** 26.1.2: distutils
- **pre-commit** 4.6.0: no-pyproject
- **propcache** 0.5.2: distutils
- **protobuf** 7.35.0: no-pyproject
- **psutil** 7.2.2: distutils
- **psycopg2-binary** 2.9.12: distutils, no-pyproject
- **ptyprocess** 0.7.0: distutils
- **pyopenssl** 26.2.0: no-build-system
- **pytest** 9.0.3: pkg-resources
- **python-dateutil** 2.9.0.post0: distutils
- **python-discovery** 1.4.0: distutils
- **pytz** 2026.2: distutils, no-pyproject, pkg-resources
- **pyyaml** 6.0.3: distutils
- **rapidfuzz** 3.14.5: distutils
- **requests-oauthlib** 2.0.0: no-pyproject
- **requests-toolbelt** 1.0.0: no-pyproject
- **s3fs** 2026.4.0: no-pyproject
- **s3transfer** 0.18.0: no-build-system
- **scipy** 1.17.1: pkg-resources
- **sentry-sdk** 2.62.0: no-build-system, pkg-resources
- **setuptools** 82.0.1: distutils, pkg-resources
- **six** 1.17.0: distutils, no-pyproject
- **smmap** 5.0.3: no-pyproject
- **snowflake-connector-python** 4.6.0: setup-cfg-deprecated-keys
- **sortedcontainers** 2.4.0: no-pyproject
- **sympy** 1.14.0: no-build-system
- **toml** 0.10.2: distutils, no-pyproject
- **transformers** 5.10.2: no-build-system
- **uritemplate** 4.2.0: no-build-system
- **uv** 0.11.19: distutils
- **uvloop** 0.22.1: pkg-resources
- **webencodings** 0.5.1: no-pyproject
- **websocket-client** 1.9.0: no-pyproject
- **werkzeug** 3.1.8: pkg-resources
- **wheel** 0.47.0: distutils
- **yarl** 1.24.2: distutils
- **ydb** 3.29.3: no-build-system
- **zstandard** 0.25.0: distutils

## errors / skips

- sglang: ScanError: sglang 0.5.12.post1 publishes no sdist

