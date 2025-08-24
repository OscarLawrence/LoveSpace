"""Find code elements commands."""

import click
from .utils import _check_code_parser


@click.group()
def find():
    """Find code elements."""
    pass


@find.command()
def analyze():
    """Analyze codebase structure."""
    if not _check_code_parser():
        click.echo("error:code_parser_not_available")
        return
    
    try:
        from knowledge.db_manager import ContextDB
        db = ContextDB()
        analysis = db.analyze_codebase()
        db.close()
        
        click.echo(f"analysis:modules:{analysis.get('modules', 0)} "
                  f"complexity:{analysis.get('avg_complexity', 0):.1f} "
                  f"coupling:{analysis.get('coupling_score', 0):.1f}")
        
    except Exception as e:
        click.echo(f"error:analysis_failed:{e}")


@find.command()
def architecture():
    """Show architectural overview."""
    if not _check_code_parser():
        click.echo("error:code_parser_not_available")
        return
    
    try:
        from knowledge.db_manager import ContextDB
        db = ContextDB()
        arch = db.get_architecture_overview()
        db.close()
        
        layers = []
        for layer, components in arch.items():
            layers.append(f"{layer}:{len(components)}")
        
        click.echo("architecture:" + ":".join(layers))
        
    except Exception as e:
        click.echo(f"error:architecture_failed:{e}")


@find.command()
def dependencies():
    """Show dependency analysis."""
    if not _check_code_parser():
        click.echo("error:code_parser_not_available")
        return
    
    try:
        from knowledge.db_manager import ContextDB
        db = ContextDB()
        deps = db.get_dependency_graph()
        db.close()
        
        external = len([d for d in deps if d.get('external', False)])
        internal = len(deps) - external
        
        click.echo(f"dependencies:external:{external}:internal:{internal}")
        
    except Exception as e:
        click.echo(f"error:dependencies_failed:{e}")


@find.command()
def patterns():
    """Show detected patterns."""
    if not _check_code_parser():
        click.echo("error:code_parser_not_available")
        return
    
    try:
        from knowledge.enhanced_patterns import EnhancedPatternDetector
        detector = EnhancedPatternDetector()
        patterns = detector.get_detected_patterns()
        
        pattern_counts = {}
        for pattern in patterns:
            ptype = pattern.get('type', 'unknown')
            pattern_counts[ptype] = pattern_counts.get(ptype, 0) + 1
        
        parts = []
        for ptype, count in pattern_counts.items():
            parts.append(f"{ptype}:{count}")
        
        click.echo("patterns:" + ":".join(parts))
        
    except Exception as e:
        click.echo(f"error:patterns_failed:{e}")


@find.command()
def gaps():
    """Find architectural gaps."""
    if not _check_code_parser():
        click.echo("error:code_parser_not_available")
        return
    
    try:
        from knowledge.db_manager import ContextDB
        db = ContextDB()
        gaps = db.find_architectural_gaps()
        db.close()
        
        gap_types = {}
        for gap in gaps:
            gtype = gap.get('type', 'unknown')
            gap_types[gtype] = gap_types.get(gtype, 0) + 1
        
        parts = []
        for gtype, count in gap_types.items():
            parts.append(f"{gtype}:{count}")
        
        click.echo("gaps:" + ":".join(parts))
        
    except Exception as e:
        click.echo(f"error:gaps_failed:{e}")


@find.command("class")
@click.argument('name')
def find_class(name):
    """Find class by name."""
    if not _check_code_parser():
        click.echo("error:code_parser_not_available")
        return
    
    try:
        from knowledge.db_manager import ContextDB
        db = ContextDB()
        classes = db.find_classes(name=name)
        db.close()
        
        if not classes:
            click.echo(f"class:{name}:not_found")
            return
        
        results = []
        for cls in classes[:5]:  # Limit to 5 results
            results.append(f"{cls.name}:{cls.file_path}:{cls.line_number}")
        
        click.echo("classes:" + ":".join(results))
        
    except Exception as e:
        click.echo(f"error:class_search_failed:{e}")


@find.command()
@click.argument('name')
def function(name):
    """Find function by name."""
    if not _check_code_parser():
        click.echo("error:code_parser_not_available")
        return
    
    try:
        from knowledge.db_manager import ContextDB
        db = ContextDB()
        functions = db.find_functions(name=name)
        db.close()
        
        if not functions:
            click.echo(f"function:{name}:not_found")
            return
        
        results = []
        for func in functions[:5]:  # Limit to 5 results
            results.append(f"{func.name}:{func.file_path}:{func.line_number}")
        
        click.echo("functions:" + ":".join(results))
        
    except Exception as e:
        click.echo(f"error:function_search_failed:{e}")