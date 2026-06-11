# Wheel/sdist divergence census

For 1,426 known-buildable packages from the top-5000 at-risk set, we built a
wheel FROM the published sdist and compared its payload byte-for-byte against
the maintainer's own published pure wheel for the same version (2026-06-12,
clean python:3.12 container; raw data results/divcheck.jsonl).

- comparable (pure wheel exists): 1185
- **byte-identical: 1087**
- **diverged: 98 (8.3% of comparable)**
- platform-wheels-only (out of scope): 234; fetch errors: 7

**Stability: all 98 divergences were independently re-run (2026-06-13); 98/98
reproduced with exact file-list agreement.** The single-package self-audit is
`wheelproof divcheck --package <name>`.

A divergence means the published wheel and published sdist of the SAME version
did not come from the same tree. Classified:

## OTHER CODE/DATA only in published wheel (dirty build tree?) (27)

- **analytics-python** 1.4.post1: segment/analytics/__init__.py, segment/analytics/client.py, segment/analytics/consumer.py
- **checkov** 3.3.1: checkov/ansible/checks/graph_checks/BlockErrorHandling.json, checkov/ansible/checks/graph_checks/DnfDisableGpgCheck.json, checkov/ansible/checks/graph_checks/DnfSslVerify.json
- **click-plugins** 1.1.1.2: click_plugins.py
- **cssbeautifier** 1.15.4: jsbeautifier/__init__.py, jsbeautifier/__version__.py, jsbeautifier/cli/__init__.py
- **django-taggit** 6.1.0: sample_taggit/__init__.py, sample_taggit/asgi.py, sample_taggit/library_management/__init__.py
- **ecdsa** 0.19.2: ecdsa/_rwlock.py, ecdsa/test_rw_lock.py
- **enum34** 1.1.10: enum/LICENSE, enum/README, enum/__init__.py
- **faker** 40.23.0: faker/sphinx/__init__.py, faker/sphinx/autodoc.py, faker/sphinx/docstring.py
- **funcy** 2.0: funcy/compat.py, funcy/py2.py, funcy/py3.py
- **geopy** 2.4.1: geopy/geocoders/algolia.py, geopy/geocoders/dot_us.py, geopy/geocoders/geocodefarm.py
- **glom** 25.12.0: glom/chainmap_backport.py, glom/reprlib_backport.py
- **gluonts** 0.16.2: gluonts/nursery/SCott/dataset_tools/algo_clustering.py, gluonts/nursery/SCott/dataset_tools/electricity.py, gluonts/nursery/SCott/dataset_tools/exchange_rate.py
- **inflection** 0.5.1: inflection.py
- **json-logic** 0.6.3: json-logic-py/__init__.py, json-logic-py/json_logic.py
- **mike** 2.2.0: mike/mkdocs.py, mike/templates/index.html, mike/themes/material/__init__.py
- **nanoid** 2.0.0: nanoid.py
- **olefile** 0.47: OleFileIO_PL.py, olefile/CONTRIBUTORS.txt, olefile/LICENSE.txt
- **pre-commit-hooks** 6.0.0: pre_commit_hooks/check_byte_order_marker.py, pre_commit_hooks/fix_encoding_pragma.py
- **pytest-ordering** 0.6: pytest_ordering.py
- **pytest-sftpserver** 1.3.0: pytest_sftpserver/autolog.py, pytest_sftpserver/sftp/virtual_sftp.py, pytest_sftpserver/sftp_old.py
- **pywinauto** 0.6.9: pywinauto/controls/__init__.py, pywinauto/controls/common_controls.py, pywinauto/controls/hwndwrapper.py
- **requests-toolbelt** 1.0.0: requests_toolbelt/adapters/appengine.py
- **rx** 3.2.0: rx/core/operators/merge_scan.py, rx/testing/testsubscriber.py
- **shareplum** 0.5.1: shareplum/ListDict.py, shareplum/shareplum.py
- **spark-nlp** 6.4.1: sparknlp/annotator/ner/llm_ner.py
- **troposphere** 4.10.2: troposphere/iotfleethub.py, troposphere/lookoutmetrics.py, troposphere/opsworkscm.py
- **webvtt-py** 0.5.1: webvtt/parsers.py, webvtt/structures.py, webvtt/writers.py

## files only in sdist build (wheel under-ships vs source) (17)

- **azure-cosmosdb-table** 1.0.6: azure/__init__.py, azure/cosmosdb/__init__.py
- **azure-mgmt-datalake-analytics** 0.6.0: azure/__init__.py, azure/mgmt/__init__.py, azure/mgmt/datalake/__init__.py
- **azure-mgmt-datalake-store** 0.5.0: azure/__init__.py, azure/mgmt/__init__.py, azure/mgmt/datalake/__init__.py
- **azure-mgmt-machinelearningcompute** 0.4.1: azure/__init__.py, azure/mgmt/__init__.py
- **cython** 3.2.5: Cython/Compiler/Code.cpython-312-x86_64-linux-gnu.so, Cython/Compiler/FlowControl.cpython-312-x86_64-linux-gnu.so, Cython/Compiler/FusedNode.cpython-312-x86_64-linux-gnu.so
- **frozenlist** 1.8.0: frozenlist/_frozenlist.cpython-312-x86_64-linux-gnu.so
- **passlib** 1.7.4: passlib/_setup/__init__.py, passlib/_setup/stamp.py
- **propcache** 0.5.2: propcache/_helpers_c.cpython-312-x86_64-linux-gnu.so
- **protobuf** 7.35.0: google/__init__.py, google/_upb/_message.cpython-312-x86_64-linux-gnu.so
- **pymemcache** 4.0.0: pymemcache/py.typed
- **pyrsistent** 0.20.0: pvectorc.cpython-312-x86_64-linux-gnu.so
- **simplejson** 4.1.1: simplejson/_speedups.cpython-312-x86_64-linux-gnu.so
- **sudachidict-core** 20260428: sudachidict_core/resources/LEGAL, sudachidict_core/resources/LICENSE-2.0.txt
- **thefuzz** 0.22.1: thefuzz/fuzz.pyi, thefuzz/process.pyi, thefuzz/py.typed
- **toml** 0.10.2: toml/__init__.pyi, toml/decoder.pyi, toml/encoder.pyi
- **uszipcode** 1.0.1: uszipcode/__pycache__/__init__.cpython-312.pyc, uszipcode/__pycache__/_version.cpython-312.pyc, uszipcode/__pycache__/search.cpython-312.pyc
- **yarl** 1.24.2: yarl/_quoting_c.cpython-312-x86_64-linux-gnu.so

## version stamps / generated code (benign) (15)

- **adlfs** 2026.5.0: adlfs/_version.py
- **aioboto3** 15.5.0: aioboto3/_version.py
- **ansi2html** 1.9.2: ansi2html/_version.py
- **cloup** 3.1.0: cloup/_version.py
- **ddsketch** 3.0.1: ddsketch/__version.py
- **facexlib** 0.3.0: facexlib/version.py
- **locate** 1.1.1: locate/version.py
- **locust-plugins** 5.0.0: locust_plugins/_version.py
- **py** 1.11.0: py/_version.py
- **pytest-cases** 3.10.1: pytest_cases/_version.py
- **pywin32-ctypes** 0.2.3: win32ctypes/version.py
- **scikit-build** 0.19.0: skbuild/_version.py
- **scikit-build-core** 0.12.2: scikit_build_core/_version.py
- **testrail-api** 1.13.6: testrail_api/__version__.py
- **yq** 3.4.3: yq/version.py

## test suite in wheel but excluded from sdist (14)

- **adagio** 0.2.6: tests/shells/__init__.py, tests/shells/test_interfaceless.py
- **aenum** 3.1.17: aenum/test_stdlib_tests.py, aenum/test_v37.py
- **bc-python-hcl2** 0.4.3: test/__init__.py, test/helpers/__init__.py, test/unit/__init__.py
- **canmatrix** 1.2: canmatrix/tests/ARXMLCompuMethod1.arxml, canmatrix/tests/ARXMLContainerTest.arxml, canmatrix/tests/ARXMLSecuredPDUTest.arxml
- **collate-sqllineage** 2.1.3: tests/corpus/__init__.py, tests/corpus/oss/__init__.py, tests/corpus/oss/test_comments.py
- **graphene** 3.4.3: graphene/relay/tests/__init__.py, graphene/relay/tests/test_connection.py, graphene/relay/tests/test_connection_async.py
- **hyperopt** 0.2.7: hyperopt/tests/test_anneal.py, hyperopt/tests/test_atpe_basic.py, hyperopt/tests/test_criteria.py
- **icecream** 2.2.0: tests/__init__.py, tests/install_test_import.py, tests/test_icecream.py
- **looker-sdk** 26.10.0: tests/integration/__init__.py, tests/integration/test_methods.py, tests/integration/test_netrc.py
- **mergedeep** 1.3.4: mergedeep/test_mergedeep.py
- **openapi-schema-pydantic** 1.2.4: tests/schema_classes/__init__.py, tests/schema_classes/test_schema.py, tests/schema_classes/test_security_scheme.py
- **segment-analytics-python** 2.3.6: segment/analytics/test/client.py, segment/analytics/test/consumer.py, segment/analytics/test/module.py
- **sendgrid** 6.12.5: test/integ/__init__.py, test/integ/test_sendgrid.py, test/unit/__init__.py
- **sqlalchemy-mate** 2.0.0.3: sqlalchemy_mate/tests/__init__.py, sqlalchemy_mate/tests/api.py, sqlalchemy_mate/tests/constants.py

## mixed/content (10)

- **botocore** 1.43.27: botocore/data/accessanalyzer/2019-11-01/endpoint-rule-set-1.json.gz, botocore/data/accessanalyzer/2019-11-01/service-2.json.gz, botocore/data/account/2021-02-01/endpoint-rule-set-1.json.gz
- **intuit-oauth** 1.2.6: intuit_oauth-1.2.6-py3.10-nspkg.pth
- **pastedeploy** 3.1.0: PasteDeploy-3.1.0-py3.11-nspkg.pth
- **publicsuffixlist** 1.0.2.20260611: publicsuffixlist/public_suffix_list.dat
- **pyarmor** 9.2.5: pyarmor/cli/core.data.2, pyarmor/cli/core.data.3, pyarmor/cli/register.py
- **pybind11** 3.0.4: pybind11/share/cmake/pybind11/pybind11Targets.cmake
- **sphinxcontrib-jsmath** 1.0.1: sphinxcontrib_jsmath-1.0.1-py3.7-nspkg.pth
- **testing-common-database** 2.0.3: testing.common.database-2.0.3-py3.6-nspkg.pth
- **testing-postgresql** 1.3.0: testing.postgresql-1.3.0-py2.7-nspkg.pth
- **usaddress** 0.5.16: usaddress/usaddr.crfsuite

## py.typed missing from sdist (source installs lose typing) (5)

- **detect-secrets** 1.5.0: detect_secrets/py.typed
- **orderedmultidict** 1.0.2: orderedmultidict/py.typed
- **rush** 2021.4.0: rush/py.typed
- **valkey** 6.1.1: valkey/py.typed
- **waybackpy** 3.0.6: waybackpy/py.typed

## BINARIES only in published wheel (not derivable from sdist) (4)

- **crypto** 1.4.1: crypto-1.4.1.data/scripts/crypto, crypto-1.4.1.data/scripts/decrypto
- **debugpy** 1.8.21: debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_cython.cp39-win_amd64.pyd, debugpy/_vendored/pydevd/_pydevd_frame_eval/pydevd_frame_evaluator.cp39-win_amd64.pyd, debugpy/_vendored/pydevd/pydevd_attach_to_process/attach.dylib
- **imagehash** 4.3.2: ImageHash-4.3.2.data/data/images/imagehash.png, ImageHash-4.3.2.data/scripts/find_similar_images.py
- **tls-client** 1.0.1: tls_client/dependencies/tls-client-32.dll, tls_client/dependencies/tls-client-64.dll, tls_client/dependencies/tls-client-amd64.so

## entry points differ (3)

- **clickclick** 20.10.2: 
- **node-semver** 0.9.0: 
- **nose** 1.3.7: nose-1.3.7.data/scripts/nosetests

## stale __pycache__/.pyc shipped in published wheel (3)

- **drf-nested-routers** 0.95.0: rest_framework_nested/__pycache__/__init__.cpython-36.pyc, rest_framework_nested/__pycache__/__init__.cpython-37.pyc, rest_framework_nested/__pycache__/relations.cpython-36.pyc
- **imapclient** 3.1.0: imapclient/__pycache__/__init__.cpython-37.pyc, imapclient/__pycache__/config.cpython-37.pyc, imapclient/__pycache__/datetime_util.cpython-37.pyc
- **suds-py3** 1.4.5.0: suds/__pycache__/__init__.cpython-38.opt-1.pyc, suds/__pycache__/builder.cpython-38.opt-1.pyc, suds/__pycache__/cache.cpython-38.opt-1.pyc

## Notable cases, stated carefully

- **debugpy 1.8.21** (Microsoft, tens of millions of dl/mo): the py3-none-any
  wheel contains compiled binaries (.pyd/.dll/.so/.dylib — vendored pydevd
  accelerators and attach helpers) that a build of the published sdist does not
  produce. This is the project's documented design, built in their CI — but it
  means the "pure" wheel's binaries are not reproducible from the published
  source artifact, which is exactly the property reproducible-builds work cares
  about. Provenance observation, not an accusation.
- **tls-client 1.0.1**: the published py3-none-any wheel contains compiled
  native libraries (.dll/.so/.dylib) that are NOT in and NOT producible from
  the published sdist. The project wraps a Go library, so bundling is its
  documented design — but it means (a) the binaries' provenance is not
  verifiable from PyPI artifacts alone, and (b) installing from source yields
  a package missing its native components. This is a provenance observation,
  not an accusation of malice.
- **drf-nested-routers, imapclient**: published wheels contain stale
  `__pycache__/*.pyc` bytecode (py3.6/3.7-era) — bytecode without matching
  review surface is a known place for things to hide, and at minimum it means
  the wheels were built from dirty working trees years ago.
- **geopy, troposphere, rx, funcy, glom**: published wheels contain Python
  modules that were apparently deleted from the project (legacy geocoders,
  removed AWS resources, py2 compat shims) — wheel users run code that source
  builders never see.
- **py.typed missing from sdists** (detect-secrets, valkey, rush, waybackpy,
  orderedmultidict): source installs silently lose type-checking support.

Caveats: 'identical' requires exact payload match; metadata drift is ignored.
Platform-wheel packages (234) are invisible to this method. The population is
the legacy-leaning at-risk set, not all of PyPI — the rate may differ in the
modern-packaging population.
