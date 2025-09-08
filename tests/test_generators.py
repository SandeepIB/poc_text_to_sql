"""Unit tests for SQL generators."""

import pytest
from text_to_sql.generators.pattern_generator import PatternSQLGenerator
from text_to_sql.generators.generator_factory import GeneratorFactory


class TestPatternGenerator:
    """Test pattern-based SQL generator."""
    
    def setup_method(self):
        """Setup test data."""
        self.schema_info = {
            "counterparty_new": type('obj', (object,), {
                'columns': [
                    {'name': 'counterparty_name', 'type': 'VARCHAR'},
                    {'name': 'counterparty_sector', 'type': 'VARCHAR'},
                    {'name': 'mpe', 'type': 'DECIMAL'}
                ]
            })(),
            "trade_new": type('obj', (object,), {
                'columns': [
                    {'name': 'notional_usd', 'type': 'DECIMAL'},
                    {'name': 'reporting_counterparty_id', 'type': 'VARCHAR'}
                ]
            })()
        }
        self.generator = PatternSQLGenerator(self.schema_info)
    
    def test_sector_lowest_exposure(self):
        """Test sector lowest exposure query."""
        question = "Which sector has the lowest exposure?"
        sql = self.generator.generate_sql(question)
        
        assert "counterparty_sector" in sql
        assert "ORDER BY" in sql
        assert "ASC" in sql
        assert "LIMIT 1" in sql
    
    def test_counterparty_highest_mpe(self):
        """Test counterparty highest MPE query."""
        question = "Which counterparties have the highest MPE?"
        sql = self.generator.generate_sql(question)
        
        assert "counterparty_name" in sql
        assert "mpe" in sql
        assert "ORDER BY" in sql
        assert "DESC" in sql


class TestGeneratorFactory:
    """Test generator factory."""
    
    def setup_method(self):
        """Setup test data."""
        self.schema_info = {"test_table": type('obj', (object,), {'columns': []})()}
        self.factory = GeneratorFactory(self.schema_info)
    
    def test_create_rule_generator(self):
        """Test creating rule-based generator."""
        generator, used = self.factory.create_generator("rule")
        assert "Rule-based" in used
        assert generator is not None
    
    def test_create_auto_generator(self):
        """Test creating auto generator."""
        generator, used = self.factory.create_generator("auto")
        assert generator is not None
        assert used is not None