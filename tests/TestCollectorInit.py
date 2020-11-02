import sys
sys.path.append('.')
import os
import unittest
from unittest import TestCase
from unittest.mock import call, patch, MagicMock
import importlib
import collectors.VMStatsCollector
from exporter import initialize_collector_by_name

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

class TestCollectorInitialization(TestCase):
    collectors.registry = CollectorRegistry()
    collectors.gateway = "prometheus-infra-pushgateway:9091"
    # collectors.gateway = "127.0.0.1:9091"


    os.environ.setdefault('TARGET', 'testhost.test')
    os.environ.setdefault('RUBRIC', 'cpu')
    collectors.VMStatsCollector.BaseCollector.get_target_tokens = MagicMock(return_value={'testhost.test': '2ed214d52'})

    @patch('BaseCollector.BaseCollector.wait_for_inventory_data')
    def test_valid_collector2(self, mocked_wait):
        mocked_wait.return_value = None
        collector = initialize_collector_by_name('VMStatsCollector')
        self.assertIsInstance(collector, collectors.VMStatsCollector.VMStatsCollector)
        g = Gauge('test_valid_collector2', 'helptext', registry=collectors.registry)
        g.set(1)
        push_to_gateway(collectors.gateway, job='bbtest', registry=collectors.registry)

    @patch('builtins.print')
    def test_with_bogus_collector(self, mocked_print):
        collector = initialize_collector_by_name('BogusCollector')
        self.assertIsNone(collector)
        self.assertEqual(mocked_print.mock_calls, [call('No Collector "BogusCollector" defined. Ignoring...')])
        g = Gauge('test_with_bogus_collector', 'helptext', registry=collectors.registry)
        g.set(1)
        push_to_gateway(collectors.gateway, job='bbtest', registry=collectors.registry)

    @patch('builtins.print')
    def test_with_invalid_collector(self, mocked_print):
        importlib.import_module = MagicMock(return_value=collectors.VMStatsCollector)
        collector = initialize_collector_by_name('ClassNotDefinedCollector')
        self.assertIsNone(collector)
        self.assertEqual(mocked_print.mock_calls, [call('Unable to initialize "ClassNotDefinedCollector". Ignoring...')])
        g = Gauge('test_with_invalid_collector', 'helptext', registry=collectors.registry)
        g.set(1)
        push_to_gateway(collectors.gateway, job='bbtest', registry=collectors.registry)


if __name__ == '__main__':
    unittest.main()
