"""NLP-enhanced SQL generator with semantic understanding."""

import re
from typing import Dict, Any, List, Set
from .base import BaseSQLGenerator


class NLPSQLGenerator(BaseSQLGenerator):
    """SQL generator with NLP understanding for semantic matching."""
    
    def __init__(self, schema_info: Dict[str, Any]):
        super().__init__(schema_info)
        self._setup_semantic_mappings()
    
    def _setup_semantic_mappings(self):
        """Setup semantic word mappings for better understanding."""
        self.synonyms = {
            # Superlative words (highest/lowest)
            'highest': ['highest', 'maximum', 'max', 'largest', 'biggest', 'most', 'top', 'greatest'],
            'lowest': ['lowest', 'minimum', 'min', 'smallest', 'least', 'bottom', 'lower', 'fewer'],
            
            # Entity words
            'counterparty': ['counterparty', 'counterparties', 'client', 'clients', 'customer', 'customers'],
            'sector': ['sector', 'sectors', 'industry', 'industries', 'segment', 'segments'],
            'trade': ['trade', 'trades', 'transaction', 'transactions', 'deal', 'deals'],
            'rating': ['rating', 'ratings', 'grade', 'grades', 'score', 'scores'],
            
            # Metric words
            'exposure': ['exposure', 'risk', 'amount', 'value', 'position'],
            'notional': ['notional', 'nominal', 'principal', 'amount', 'value'],
            'mpe': ['mpe', 'maximum potential exposure', 'max exposure', 'potential exposure'],
            
            # Action words
            'breach': ['breach', 'breached', 'exceed', 'exceeded', 'violate', 'violated', 'over', 'above'],
            'count': ['count', 'number', 'total', 'how many', 'quantity'],
            'distribution': ['distribution', 'breakdown', 'split', 'allocation', 'spread'],
            'average': ['average', 'avg', 'mean', 'typical']
        }
        
        # Create reverse mapping for fast lookup
        self.word_to_concept = {}
        for concept, words in self.synonyms.items():
            for word in words:
                self.word_to_concept[word] = concept
    
    def generate_sql(self, question: str) -> str:
        """Generate SQL with NLP understanding."""
        # Normalize and extract concepts
        concepts = self._extract_concepts(question)
        
        # Determine query type based on concepts
        if self._is_top_bottom_query(concepts):
            return self._build_top_bottom_query(question, concepts)
        
        if self._is_aggregation_query(concepts):
            return self._build_aggregation_query(concepts)
        
        if self._is_count_query(concepts):
            return self._build_count_query(concepts)
        
        if self._is_breach_query(concepts):
            return self._build_breach_query()
        
        if self._is_distribution_query(concepts):
            return self._build_distribution_query(concepts)
        
        # Default fallback
        return self._build_default_query(concepts)
    
    def _extract_concepts(self, question: str) -> Set[str]:
        """Extract semantic concepts from question."""
        words = re.findall(r'\b\w+\b', question.lower())
        concepts = set()
        
        for word in words:
            if word in self.word_to_concept:
                concepts.add(self.word_to_concept[word])
            else:
                concepts.add(word)  # Keep original word if no mapping
        
        return concepts
    
    def _is_top_bottom_query(self, concepts: Set[str]) -> bool:
        """Check if this is a top/bottom ranking query."""
        return ('highest' in concepts or 'lowest' in concepts) and \
               ('counterparty' in concepts or 'sector' in concepts or 'rating' in concepts)
    
    def _is_aggregation_query(self, concepts: Set[str]) -> bool:
        """Check if this is an aggregation query."""
        return 'average' in concepts or \
               (('highest' in concepts or 'lowest' in concepts) and 
                ('exposure' in concepts or 'notional' in concepts))
    
    def _is_count_query(self, concepts: Set[str]) -> bool:
        """Check if this is a count query."""
        return 'count' in concepts or 'how' in concepts or 'many' in concepts
    
    def _is_breach_query(self, concepts: Set[str]) -> bool:
        """Check if this is a breach/limit query."""
        return 'breach' in concepts or 'limit' in concepts
    
    def _is_distribution_query(self, concepts: Set[str]) -> bool:
        """Check if this is a distribution query."""
        return 'distribution' in concepts
    
    def _build_top_bottom_query(self, question: str, concepts: Set[str]) -> str:
        """Build top/bottom ranking query."""
        # Extract number
        num_match = re.search(r'\d+', question)
        limit = num_match.group(0) if num_match else '10'
        
        # Determine order
        order = 'ASC' if 'lowest' in concepts else 'DESC'
        
        # Determine entity and metric
        if 'counterparty' in concepts and 'mpe' in concepts:
            return f"""SELECT 
    counterparty_name, 
    counterparty_id, 
    CAST(mpe AS DECIMAL(15,2)) as mpe_value 
FROM counterparty_new 
ORDER BY CAST(mpe AS DECIMAL(15,2)) {order} 
LIMIT {limit};"""
        
        elif 'counterparty' in concepts and 'notional' in concepts:
            return f"""SELECT 
    cp.counterparty_name, 
    SUM(CAST(t.notional_usd AS DECIMAL(15,2))) as total_notional 
FROM counterparty_new cp 
JOIN trade_new t ON cp.counterparty_id = t.reporting_counterparty_id 
GROUP BY cp.counterparty_id, cp.counterparty_name 
ORDER BY total_notional {order} 
LIMIT 20;"""
        
        elif 'sector' in concepts and 'exposure' in concepts:
            return f"""SELECT 
    counterparty_sector, 
    SUM(CAST(mpe AS DECIMAL(15,2))) as total_exposure 
FROM counterparty_new 
WHERE counterparty_sector IS NOT NULL 
GROUP BY counterparty_sector 
ORDER BY total_exposure {order} 
LIMIT 1;"""
        
        elif 'rating' in concepts and 'notional' in concepts:
            return f"""SELECT 
    cp.internal_rating, 
    SUM(CAST(t.notional_usd AS DECIMAL(15,2))) as total_notional 
FROM counterparty_new cp 
JOIN trade_new t ON cp.counterparty_id = t.reporting_counterparty_id 
GROUP BY cp.internal_rating 
ORDER BY total_notional {order} 
LIMIT 1;"""
        
        return self._build_default_query(concepts)
    
    def _build_aggregation_query(self, concepts: Set[str]) -> str:
        """Build aggregation query."""
        if 'average' in concepts and 'sector' in concepts:
            return """SELECT 
    cp.counterparty_sector, 
    AVG(CAST(t.notional_usd AS DECIMAL(15,2))) as avg_notional 
FROM trade_new t 
JOIN counterparty_new cp ON t.reporting_counterparty_id = cp.counterparty_id 
WHERE cp.counterparty_sector IS NOT NULL 
GROUP BY cp.counterparty_sector 
ORDER BY avg_notional DESC;"""
        
        return self._build_default_query(concepts)
    
    def _build_count_query(self, concepts: Set[str]) -> str:
        """Build count query."""
        if 'trade' in concepts and 'counterparty' in concepts:
            return """SELECT 
    cp.counterparty_name, 
    COUNT(t.id) as trade_count 
FROM counterparty_new cp 
LEFT JOIN trade_new t ON cp.counterparty_id = t.reporting_counterparty_id 
GROUP BY cp.counterparty_id, cp.counterparty_name 
ORDER BY trade_count DESC;"""
        
        return self._build_default_query(concepts)
    
    def _build_breach_query(self) -> str:
        """Build breach/limit query."""
        return """SELECT 
    counterparty_name, 
    CAST(mpe AS DECIMAL(15,2)) as current_mpe, 
    CAST(mpe_limit AS DECIMAL(15,2)) as mpe_limit 
FROM counterparty_new 
WHERE CAST(mpe AS DECIMAL(15,2)) > CAST(mpe_limit AS DECIMAL(15,2)) 
ORDER BY current_mpe DESC;"""
    
    def _build_distribution_query(self, concepts: Set[str]) -> str:
        """Build distribution query."""
        if 'rating' in concepts:
            return """SELECT 
    internal_rating, 
    COUNT(*) as count, 
    SUM(CAST(mpe AS DECIMAL(15,2))) as total_exposure 
FROM counterparty_new 
WHERE internal_rating IS NOT NULL 
GROUP BY internal_rating 
ORDER BY total_exposure DESC;"""
        
        return self._build_default_query(concepts)
    
    def _build_default_query(self, concepts: Set[str]) -> str:
        """Build default query based on concepts."""
        if 'counterparty' in concepts:
            return "SELECT * FROM counterparty_new LIMIT 20;"
        elif 'trade' in concepts:
            return "SELECT * FROM trade_new LIMIT 20;"
        else:
            return "SELECT * FROM concentration_new LIMIT 20;"