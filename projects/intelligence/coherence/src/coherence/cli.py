#!/usr/bin/env python3
"""
Coherence Engine CLI - Test and demonstrate coherence validation capabilities.
"""

import argparse
import sys
from typing import List
from . import (
    validate_statement, 
    validate_reasoning, 
    start_coherence_monitoring,
    get_coherence_engine,
    CoherenceLevel
)


def test_statement(statement: str, monitor: bool = False):
    """Test a single statement for coherence"""
    print(f"\n🔍 Testing Statement:")
    print(f"   {statement}")
    print("-" * 60)
    
    result = validate_statement(statement, monitor=monitor)
    
    print(f"Coherence Level: {result.level.name}")
    print(f"Score: {result.score:.3f}")
    print(f"Confidence: {result.confidence:.3f}")
    
    if result.contradictions:
        print(f"\n⚠️  Contradictions Found:")
        for contradiction in result.contradictions:
            print(f"   • {contradiction}")
    else:
        print("\n✅ No contradictions detected")
    
    return result


def test_reasoning_chain(steps: List[str], monitor: bool = False):
    """Test a reasoning chain for coherence"""
    print(f"\n🔗 Testing Reasoning Chain:")
    for i, step in enumerate(steps, 1):
        print(f"   {i}. {step}")
    print("-" * 60)
    
    result = validate_reasoning(steps, monitor=monitor)
    
    print(f"Coherence Level: {result.level.name}")
    print(f"Score: {result.score:.3f}")
    print(f"Confidence: {result.confidence:.3f}")
    
    if result.contradictions:
        print(f"\n⚠️  Contradictions Found:")
        for contradiction in result.contradictions:
            print(f"   • {contradiction}")
    else:
        print("\n✅ No contradictions detected")
    
    return result


def run_demo():
    """Run a demonstration of coherence validation"""
    print("🎯 Coherence Engine Demo")
    print("=" * 60)
    
    # Test coherent statement
    test_statement("The system validates logical consistency to ensure reliable reasoning.")
    
    # Test incoherent statement
    test_statement("This statement is always true and never false, but it's impossible to verify.")
    
    # Test coherent reasoning chain
    coherent_reasoning = [
        "We need to build coherent AI tools",
        "Coherent tools require logical consistency validation", 
        "Therefore, we must first build a coherence engine",
        "The coherence engine will enable building truly coherent tools"
    ]
    test_reasoning_chain(coherent_reasoning)
    
    # Test incoherent reasoning chain
    incoherent_reasoning = [
        "All AI systems are perfectly logical",
        "Current AI systems contain contradictions",
        "Therefore, no AI systems exist",
        "But we are using an AI system right now"
    ]
    test_reasoning_chain(incoherent_reasoning)


def run_interactive():
    """Run interactive coherence testing"""
    print("🔍 Interactive Coherence Validator")
    print("=" * 40)
    print("Enter statements or reasoning steps to validate.")
    print("Commands:")
    print("  'quit' or 'exit' - Exit")
    print("  'demo' - Run demonstration")
    print("  'stats' - Show monitoring statistics")
    print("  'monitor on/off' - Toggle monitoring")
    print()
    
    engine = get_coherence_engine()
    monitoring = False
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                break
            elif user_input.lower() == 'demo':
                run_demo()
            elif user_input.lower() == 'stats':
                if monitoring:
                    stats = engine.get_monitoring_stats()
                    print(f"\n📊 Monitoring Statistics:")
                    print(f"   Total Validations: {stats['total_validations']}")
                    print(f"   Average Coherence: {stats['average_coherence']:.3f}")
                    print(f"   Trend: {stats['trend_direction']}")
                else:
                    print("⚠️  Monitoring is not enabled. Use 'monitor on' to start.")
            elif user_input.lower() == 'monitor on':
                engine.start_monitoring()
                monitoring = True
                print("✅ Monitoring enabled")
            elif user_input.lower() == 'monitor off':
                engine.stop_monitoring()
                monitoring = False
                print("⏹️  Monitoring disabled")
            elif user_input:
                # Check if it looks like a reasoning chain (contains numbers or arrows)
                if any(marker in user_input for marker in ['1.', '2.', '->', '=>', 'then', 'therefore']):
                    # Try to parse as reasoning steps
                    steps = []
                    for line in user_input.split('.'):
                        line = line.strip()
                        if line and not line.isdigit():
                            # Remove numbering
                            line = line.lstrip('0123456789. ')
                            if line:
                                steps.append(line)
                    
                    if len(steps) > 1:
                        test_reasoning_chain(steps, monitor=monitoring)
                    else:
                        test_statement(user_input, monitor=monitoring)
                else:
                    test_statement(user_input, monitor=monitoring)
                    
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Coherence Engine CLI")
    parser.add_argument("--demo", action="store_true", help="Run demonstration")
    parser.add_argument("--interactive", action="store_true", help="Run interactive mode")
    parser.add_argument("--statement", type=str, help="Test a single statement")
    parser.add_argument("--monitor", action="store_true", help="Enable monitoring")
    
    args = parser.parse_args()
    
    if args.demo:
        run_demo()
    elif args.statement:
        test_statement(args.statement, monitor=args.monitor)
    elif args.interactive:
        run_interactive()
    else:
        # Default to interactive mode
        run_interactive()


if __name__ == "__main__":
    main()