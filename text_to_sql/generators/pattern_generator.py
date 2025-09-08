"""Pattern-based SQL generator using keyword matching."""

from typing import Dict, Any
from .base import BaseSQLGenerator


class PatternSQLGenerator(BaseSQLGenerator):
    """SQL generator using pattern matching on keywords."""
    
    def generate_sql(self, question: str) -> str:
        """Generate SQL query based on keyword patterns."""
        q = question.lower()
        
        # Top counterparties by MPE
        if self._matches_pattern(q, ['top', 'counterpart', 'mpe']):
            num = self._extract_number(q, default='10')
            return self._build_top_counterparties_mpe_query(num)
        
        # Rating and notional queries
        if self._matches_pattern(q, ['rating', 'highest', 'notional']):
            return self._build_rating_notional_query()
        
        # Counterparty notional queries
        if self._matches_pattern(q, ['counterpart', 'highest', 'notional']):
            return self._build_counterparty_notional_query('DESC')
        
        if self._matches_pattern(q, ['counterpart', 'lowest', 'notional']):
            return self._build_counterparty_notional_query('ASC')
        
        # Trade count queries
        if self._matches_pattern(q, ['how many trades', 'counterpart']):
            return self._build_trade_count_query()
        
        # Single trade queries
        if self._matches_pattern(q, ['highest', 'trade', 'notional']):
            return self._build_highest_trade_query()
        
        # Limit breach queries
        if self._matches_any(q, ['breach', 'limit']):
            return self._build_limit_breach_query()
        
        # Distribution queries
        if self._matches_pattern(q, ['distribution', 'rating']):
            return self._build_rating_distribution_query()
        
        # Concentration group queries
        if self._matches_any_pattern(q, [
            ['concentration', 'group', 'lowest', 'exposure'],
            ['concentration', 'group', 'minimum', 'exposure'],
            ['concentration', 'lowest', 'aggregate']
        ]):
            return self._build_concentration_group_query('ASC')
        
        if self._matches_any_pattern(q, [
            ['concentration', 'group', 'highest', 'exposure'],
            ['concentration', 'group', 'maximum', 'exposure']
        ]):
            return self._build_concentration_group_query('DESC')
        
        # Sector queries
        if self._matches_pattern(q, ['average', 'sector', 'notional']):
            return self._build_sector_average_query()
        
        if self._matches_any_pattern(q, [
            ['sector', 'lowest', 'exposure'],
            ['sector', 'minimum', 'exposure'],
            ['sector', 'smallest', 'exposure'],
            ['sector', 'least', 'exposure']
        ]):
            return self._build_sector_exposure_query('ASC')
        
        if self._matches_any_pattern(q, [
            ['sector', 'highest', 'exposure'],
            ['sector', 'largest', 'exposure'],
            ['sector', 'concentration', 'exposure']
        ]):
            return self._build_sector_exposure_query('DESC')
        
        # Default queries
        return self._build_default_query(q)
    
    def _matches_pattern(self, text: str, keywords: list) -> bool:
        """Check if all keywords are present in text."""
        return all(keyword in text for keyword in keywords)
    
    def _matches_any(self, text: str, keywords: list) -> bool:
        """Check if any keyword is present in text."""
        return any(keyword in text for keyword in keywords)
    
    def _matches_any_pattern(self, text: str, patterns: list) -> bool:
        """Check if any pattern matches."""
        return any(self._matches_pattern(text, pattern) for pattern in patterns)
    
    def _extract_number(self, text: str, default: str = '10') -> str:
        """Extract number from text."""
        import re
        match = re.search(r'\d+', text)
        return match.group(0) if match else default
    
    def _build_top_counterparties_mpe_query(self, limit: str) -> str:
        """Build query for top counterparties by MPE."""
        return f"""SELECT 
    counterparty_name, 
    counterparty_id, 
    CAST(mpe AS DECIMAL(15,2)) as mpe_value 
FROM counterparty_new 
ORDER BY CAST(mpe AS DECIMAL(15,2)) DESC 
LIMIT {limit};"""
    
    def _build_rating_notional_query(self) -> str:
        """Build query for rating with highest notional."""
        return """SELECT 
    cp.internal_rating, 
    SUM(CAST(t.notional_usd AS DECIMAL(15,2))) as total_notional 
FROM counterparty_new cp 
JOIN trade_new t ON cp.counterparty_id = t.reporting_counterparty_id 
GROUP BY cp.internal_rating 
ORDER BY total_notional DESC 
LIMIT 1;"""
    
    def _build_counterparty_notional_query(self, order: str) -> str:
        """Build query for counterparty notional exposure."""
        return f"""SELECT 
    cp.counterparty_name, 
    SUM(CAST(t.notional_usd AS DECIMAL(15,2))) as total_notional 
FROM counterparty_new cp 
JOIN trade_new t ON cp.counterparty_id = t.reporting_counterparty_id 
GROUP BY cp.counterparty_id, cp.counterparty_name 
ORDER BY total_notional {order} 
LIMIT 20;"""
    
    def _build_trade_count_query(self) -> str:
        """Build query for trade count per counterparty."""
        return """SELECT 
    cp.counterparty_name, 
    COUNT(t.id) as trade_count 
FROM counterparty_new cp 
LEFT JOIN trade_new t ON cp.counterparty_id = t.reporting_counterparty_id 
GROUP BY cp.counterparty_id, cp.counterparty_name 
ORDER BY trade_count DESC;"""
    
    def _build_highest_trade_query(self) -> str:
        """Build query for highest single trade."""
        return """SELECT 
    t.trade_id, 
    cp.counterparty_name, 
    t.notional_usd, 
    t.currency 
FROM trade_new t 
JOIN counterparty_new cp ON t.reporting_counterparty_id = cp.counterparty_id 
ORDER BY CAST(t.notional_usd AS DECIMAL(15,2)) DESC 
LIMIT 1;"""
    
    def _build_limit_breach_query(self) -> str:
        """Build query for limit breaches."""
        return """SELECT 
    counterparty_name, 
    CAST(mpe AS DECIMAL(15,2)) as current_mpe, 
    CAST(mpe_limit AS DECIMAL(15,2)) as mpe_limit 
FROM counterparty_new 
WHERE CAST(mpe AS DECIMAL(15,2)) > CAST(mpe_limit AS DECIMAL(15,2)) 
ORDER BY current_mpe DESC;"""
    
    def _build_rating_distribution_query(self) -> str:
        """Build query for rating distribution."""
        return """SELECT 
    internal_rating, 
    COUNT(*) as count, 
    SUM(CAST(mpe AS DECIMAL(15,2))) as total_exposure 
FROM counterparty_new 
WHERE internal_rating IS NOT NULL 
GROUP BY internal_rating 
ORDER BY total_exposure DESC;"""
    
    def _build_sector_average_query(self) -> str:
        """Build query for sector average notional."""
        return """SELECT 
    cp.counterparty_sector, 
    AVG(CAST(t.notional_usd AS DECIMAL(15,2))) as avg_notional 
FROM trade_new t 
JOIN counterparty_new cp ON t.reporting_counterparty_id = cp.counterparty_id 
WHERE cp.counterparty_sector IS NOT NULL 
GROUP BY cp.counterparty_sector 
ORDER BY avg_notional DESC;"""
    
    def _build_sector_exposure_query(self, order: str) -> str:
        """Build query for sector exposure."""
        return f"""SELECT 
    counterparty_sector, 
    SUM(CAST(mpe AS DECIMAL(15,2))) as total_exposure 
FROM counterparty_new 
WHERE counterparty_sector IS NOT NULL 
GROUP BY counterparty_sector 
ORDER BY total_exposure {order} 
LIMIT 1;"""
    
    def _build_concentration_group_query(self, order: str) -> str:
        """Build query for concentration group exposure."""
        return f"""SELECT 
    concentration_group, 
    SUM(CAST(concentration_value AS DECIMAL(15,2))) as total_exposure 
FROM concentration_new 
WHERE concentration_group IS NOT NULL 
GROUP BY concentration_group 
ORDER BY total_exposure {order} 
LIMIT 1;"""
    
    def _build_default_query(self, question: str) -> str:
        """Build default query based on keywords."""
        if 'concentration' in question:
            return "SELECT * FROM concentration_new LIMIT 20;"
        elif 'counterpart' in question:
            return "SELECT * FROM counterparty_new LIMIT 20;"
        elif 'trade' in question:
            return "SELECT * FROM trade_new LIMIT 20;"
        else:
            return "SELECT * FROM concentration_new LIMIT 20;"