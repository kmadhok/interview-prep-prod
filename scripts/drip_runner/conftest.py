import os
import sys

# Put this package dir on sys.path so the test modules' top-level imports
# (`import job_parser`, `import dedupe`) resolve when pytest is run from the
# repo root (e.g. in CI), not only from inside scripts/drip_runner/.
sys.path.insert(0, os.path.dirname(__file__))
