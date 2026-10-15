from pathlib import Path
import importlib.util
import json
import shutil
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('validator',ROOT/'scripts/validate_skill.py')
validator=importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class StandardTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        for name in ('README.md','SKILL.md','CONTRIBUTING.md','shuku.json','.template'):
            if (ROOT/name).exists():
                shutil.copyfile(ROOT/name,self.root/name)
        value=json.loads((self.root/'shuku.json').read_text(encoding='utf-8'))
        entry=value.get('entry','SKILL.md')
        if entry!='SKILL.md':
            entry=(self.root/value.get('path','.'))/entry
            entry.parent.mkdir(parents=True,exist_ok=True)
            entry.write_text('<h1>Fixture course</h1>',encoding='utf-8')

    def test_standard_and_missing_entry(self):
        self.assertEqual(validator.validate(self.root),[])
        value=json.loads((self.root/'shuku.json').read_text(encoding='utf-8'))
        value['entry']='missing.html'
        (self.root/'shuku.json').write_text(json.dumps(value),encoding='utf-8')
        self.assertTrue(validator.validate(self.root))

    def test_legacy_descriptor_rejected(self):
        (self.root/'course.yaml').write_text('{}',encoding='utf-8')
        self.assertTrue(validator.validate(self.root))

    @unittest.skipUnless((ROOT/'.template').exists(),'Only the template has an initializer')
    def test_initialization_escapes_metadata_and_is_not_repeatable(self):
        spec=importlib.util.spec_from_file_location('initializer',ROOT/'scripts/init_skill.py')
        initializer=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(initializer)
        initializer.initialize(self.root,'test-course','Course "Title"','Learn: "quoted" text','https://github.com/reduct-shuku/test-course')
        self.assertFalse((self.root/'.template').exists())
        self.assertEqual(validator.validate(self.root),[])
        self.assertEqual(json.loads((self.root/'shuku.json').read_text(encoding='utf-8'))['title'],'Course "Title"')
        with self.assertRaises(ValueError):
            initializer.initialize(self.root,'test-course','Course','Learn','https://github.com/reduct-shuku/test-course')


if __name__=='__main__':
    unittest.main()
