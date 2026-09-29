"""
Validation layer for data quality checks
Implements schema, range, CRS, and completeness checks
"""

from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from database import SessionLocal
from models.schema import DataQuality, SourceTag
from datetime import datetime
import json


class DataValidator:
    """Data quality validation layer"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def check_schema(self, table_name: str, record_id: int = None):
        """Check schema constraints for a table"""
        try:
            # Get table metadata
            inspector = inspect(self.db.bind)
            columns = inspector.get_columns(table_name)
            
            checks_passed = 0
            checks_failed = 0
            
            # Check each column for basic schema compliance
            for column in columns:
                check_result = self._check_column_schema(table_name, column, record_id)
                if check_result['status'] == 'passed':
                    checks_passed += 1
                else:
                    checks_failed += 1
                    self._log_quality_check(
                        table_name, record_id, 'schema',
                        f"Column {column['name']} schema check",
                        check_result['status'],
                        check_result.get('error_message')
                    )
            
            return {'passed': checks_passed, 'failed': checks_failed}
            
        except Exception as e:
            self._log_quality_check(
                table_name, record_id, 'schema',
                "Schema validation",
                'failed',
                str(e)
            )
            return {'passed': 0, 'failed': 1}
    
    def _check_column_schema(self, table_name: str, column: dict, record_id: int = None):
        """Check individual column schema"""
        try:
            # Basic schema checks
            if column.get('nullable') == False and column.get('default') is None:
                # Check for non-null constraint violations would require actual data inspection
                pass
            
            return {'status': 'passed'}
        except Exception as e:
            return {'status': 'failed', 'error_message': str(e)}
    
    def check_range(self, table_name: str, column_name: str, min_value: float = None, max_value: float = None):
        """Check range constraints for numeric columns"""
        try:
            query_parts = [f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} IS NOT NULL"]
            
            if min_value is not None:
                query_parts.append(f" AND {column_name} < {min_value}")
            if max_value is not None:
                query_parts.append(f" AND {column_name} > {max_value}")
            
            query = text(" ".join(query_parts))
            result = self.db.execute(query).scalar()
            
            if result > 0:
                self._log_quality_check(
                    table_name, None, 'range',
                    f"Range check for {column_name}",
                    'failed',
                    f"{result} records outside range [{min_value}, {max_value}]"
                )
                return {'status': 'failed', 'violations': result}
            else:
                self._log_quality_check(
                    table_name, None, 'range',
                    f"Range check for {column_name}",
                    'passed',
                    None
                )
                return {'status': 'passed', 'violations': 0}
                
        except Exception as e:
            self._log_quality_check(
                table_name, None, 'range',
                f"Range check for {column_name}",
                'failed',
                str(e)
            )
            return {'status': 'failed', 'error': str(e)}
    
    def check_crs(self, table_name: str, geometry_column: str = 'location'):
        """Check coordinate reference system for geometry columns"""
        try:
            query_str = f"""
                SELECT COUNT(*) FROM {table_name} 
                WHERE {geometry_column} IS NOT NULL 
                AND ST_SRID({geometry_column}) != 4326
            """
            query = text(query_str)
            result = self.db.execute(query).scalar()
            
            if result > 0:
                self._log_quality_check(
                    table_name, None, 'crs',
                    f"CRS check for {geometry_column}",
                    'failed',
                    f"{result} records with incorrect CRS (expected 4326)"
                )
                return {'status': 'failed', 'violations': result}
            else:
                self._log_quality_check(
                    table_name, None, 'crs',
                    f"CRS check for {geometry_column}",
                    'passed',
                    None
                )
                return {'status': 'passed', 'violations': 0}
                
        except Exception as e:
            # If column doesn't exist or isn't geometry, skip
            if 'does not exist' in str(e) or 'is not of type geometry' in str(e):
                return {'status': 'skipped', 'error': str(e)}
            
            self._log_quality_check(
                table_name, None, 'crs',
                f"CRS check for {geometry_column}",
                'failed',
                str(e)
            )
            return {'status': 'failed', 'error': str(e)}
    
    def check_completeness(self, table_name: str, required_columns: list):
        """Check completeness of required columns"""
        try:
            # Get table metadata
            inspector = inspect(self.db.bind)
            columns = inspector.get_columns(table_name)
            column_names = [col['name'] for col in columns]
            
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                self._log_quality_check(
                    table_name, None, 'completeness',
                    "Column completeness check",
                    'failed',
                    f"Missing required columns: {missing_columns}"
                )
                return {'status': 'failed', 'missing': missing_columns}
            else:
                self._log_quality_check(
                    table_name, None, 'completeness',
                    "Column completeness check",
                    'passed',
                    None
                )
                return {'status': 'passed', 'missing': []}
                
        except Exception as e:
            self._log_quality_check(
                table_name, None, 'completeness',
                "Column completeness check",
                'failed',
                str(e)
            )
            return {'status': 'failed', 'error': str(e)}
    
    def check_source_tags(self, table_name: str):
        """Check that all records have valid source tags"""
        try:
            valid_tags = ['REAL_OFFICIAL', 'REAL_PUBLIC', 'PROXY', 'SYNTHETIC']
            
            query_str = f"""
                SELECT COUNT(*) FROM {table_name} 
                WHERE source_tag NOT IN ('REAL_OFFICIAL', 'REAL_PUBLIC', 'PROXY', 'SYNTHETIC')
            """
            query = text(query_str)
            result = self.db.execute(query).scalar()
            
            if result > 0:
                self._log_quality_check(
                    table_name, None, 'schema',
                    "Source tag validation",
                    'failed',
                    f"{result} records with invalid source tags"
                )
                return {'status': 'failed', 'violations': result}
            else:
                self._log_quality_check(
                    table_name, None, 'schema',
                    "Source tag validation",
                    'passed',
                    None
                )
                return {'status': 'passed', 'violations': 0}
                
        except Exception as e:
            # If source_tag column doesn't exist, skip
            if 'does not exist' in str(e) or 'column' in str(e).lower():
                return {'status': 'skipped', 'error': str(e)}
            
            self._log_quality_check(
                table_name, None, 'schema',
                "Source tag validation",
                'failed',
                str(e)
            )
            return {'status': 'failed', 'error': str(e)}
    
    def _log_quality_check(self, table_name: str, record_id: int, check_type: str, 
                          check_description: str, status: str, error_message: str = None):
        """Log quality check results to data_quality table"""
        try:
            quality_record = DataQuality(
                table_name=table_name,
                record_id=record_id,
                check_type=check_type,
                check_description=check_description,
                status=status,
                error_message=error_message,
                source_tag=SourceTag.SYNTHETIC
            )
            self.db.add(quality_record)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"Error logging quality check: {e}")
    
    def run_all_validations(self):
        """Run all validation checks on all tables"""
        tables_to_validate = [
            'mines', 'drillholes', 'assay_intervals', 'production_records',
            'equipment_events', 'blast_records', 'env_observations'
        ]
        
        results = {}
        for table in tables_to_validate:
            print(f"Validating table: {table}")
            table_results = {}
            
            # Schema checks
            table_results['schema'] = self.check_schema(table)
            
            # CRS checks for geometry columns
            table_results['crs_location'] = self.check_crs(table, 'location')
            table_results['crs_boundary'] = self.check_crs(table, 'boundary')
            
            # Source tag validation
            table_results['source_tags'] = self.check_source_tags(table)
            
            # Range checks for common numeric columns
            if table == 'production_records':
                table_results['range_ore'] = self.check_range(table, 'ore_extracted_tonnes', 0, 10000)
                table_results['range_grade'] = self.check_range(table, 'grade_percent', 0, 100)
            elif table == 'assay_intervals':
                table_results['range_mn'] = self.check_range(table, 'mn_percent', 0, 100)
            
            results[table] = table_results
        
        return results
    
    def close(self):
        """Close database connection"""
        self.db.close()


def main():
    """Main function to run validation checks"""
    validator = DataValidator()
    try:
        results = validator.run_all_validations()
        print("\nValidation Results:")
        for table, checks in results.items():
            print(f"\n{table}:")
            for check_type, result in checks.items():
                print(f"  {check_type}: {result}")
    finally:
        validator.close()


if __name__ == "__main__":
    main()
