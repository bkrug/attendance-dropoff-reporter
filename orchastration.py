import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from report_orchastrator import ReportOrchastrator

ReportOrchastrator().generate_report()

