import pytest
from data_pipelines.definition.cedict import get_version
from data_pipelines.definition.versions import DictionaryVersion

dummy_response = """
<p class="description">
Latest release: <strong>2021-01-13 06:31:04 GMT</strong>
<br>
Number of entries: <strong>118981</strong>
<br>
<strong><a href="export/cedict/cedict_1_0_ts_utf-8_mdbg.zip">cedict_1_0_ts_utf-8_mdbg.zip</a></strong> - CC-CEDICT in UTF-8, with both traditional and simplified Chinese (ZIP archive format)
<br>
<strong><a href="export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz">cedict_1_0_ts_utf-8_mdbg.txt.gz</a></strong> - CC-CEDICT in UTF-8, with both traditional and simplified Chinese (GZip format)
</p>
"""


def test_can_get_version(requests_mock):
    requests_mock.get('https://www.mdbg.net/chinese/dictionary?page=cedict', text=dummy_response)
    version = get_version.run()

    assert version.version_name == "2021-01-13 06:31:04 GMT"
    assert version.entries == "118981"
    assert version.link == "https://www.mdbg.net/export/cedict/cedict_1_0_ts_utf-8_mdbg.zip"