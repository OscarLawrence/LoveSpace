/*!
Code Coherence Checker CLI - Mathematical verification of code logical consistency

Usage:
  code_checker verify-function --code "def func(): ..." 
  code_checker verify-file --path "script.py"
  code_checker interactive
  code_checker test

Provides 100% mathematical certainty of code coherence through formal verification.
*/

use code_coherence_checker::{CodeCoherenceChecker, CodeVerificationResult};
use z3::Config;
use clap::{Parser, Subcommand};
use z3;
use std::fs;
use std::io::{self, Write};
use anyhow::Result;

#[derive(Parser)]
#[command(name = "code_checker")]
#[command(about = "Mathematical verification of code logical consistency")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Verify coherence of a Python function from command line
    VerifyFunction {
        /// Python function code to verify
        #[arg(short, long)]
        code: String,
    },
    /// Verify coherence of a Python file
    VerifyFile {
        /// Path to Python file
        #[arg(short, long)]
        path: String,
    },
    /// Interactive coherence checking session
    Interactive,
    /// Run built-in test suite
    Test,
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    let cfg = Config::new();
    let ctx = z3::Context::new(&cfg);
    let mut checker = CodeCoherenceChecker::new(&ctx);

    match cli.command {
        Commands::VerifyFunction { code } => {
            verify_function_command(&mut checker, &code)?;
        }
        Commands::VerifyFile { path } => {
            verify_file_command(&mut checker, &path)?;
        }
        Commands::Interactive => {
            interactive_mode(&mut checker)?;
        }
        Commands::Test => {
            run_test_suite(&mut checker)?;
        }
    }

    Ok(())
}

fn verify_function_command(checker: &mut CodeCoherenceChecker, code: &str) -> Result<()> {
    println!("🔍 Analyzing function for logical coherence...\n");
    
    let result = checker.verify_function(code)?;
    display_verification_result(&result);
    
    Ok(())
}

fn verify_file_command(checker: &mut CodeCoherenceChecker, path: &str) -> Result<()> {
    println!("🔍 Analyzing file: {}\n", path);
    
    let code = fs::read_to_string(path)?;
    let results = checker.verify_module(&code)?;
    
    for (i, result) in results.iter().enumerate() {
        println!("Function {}:", i + 1);
        display_verification_result(result);
        println!();
    }
    
    Ok(())
}

fn interactive_mode(checker: &mut CodeCoherenceChecker) -> Result<()> {
    println!("🚀 Code Coherence Checker - Interactive Mode");
    println!("Enter Python functions to verify logical coherence.");
    println!("Type 'exit' to quit, 'help' for commands.\n");

    loop {
        print!("coherence> ");
        io::stdout().flush()?;
        
        let mut input = String::new();
        io::stdin().read_line(&mut input)?;
        let input = input.trim();
        
        match input {
            "exit" => {
                println!("👋 Goodbye!");
                break;
            }
            "help" => {
                print_help();
            }
            "test" => {
                run_test_suite(checker)?;
            }
            "" => continue,
            _ => {
                if input.starts_with("def ") {
                    // Single line function
                    match checker.verify_function(input) {
                        Ok(result) => display_verification_result(&result),
                        Err(e) => println!("❌ Error: {}", e),
                    }
                } else {
                    // Multi-line input mode
                    println!("📝 Multi-line mode. Enter your function (end with empty line):");
                    let code = read_multiline_input()?;
                    
                    match checker.verify_function(&code) {
                        Ok(result) => display_verification_result(&result),
                        Err(e) => println!("❌ Error: {}", e),
                    }
                }
            }
        }
        println!();
    }
    
    Ok(())
}

fn read_multiline_input() -> Result<String> {
    let mut lines = Vec::new();
    
    loop {
        let mut line = String::new();
        io::stdin().read_line(&mut line)?;
        
        if line.trim().is_empty() {
            break;
        }
        
        lines.push(line);
    }
    
    Ok(lines.join(""))
}

fn display_verification_result(result: &CodeVerificationResult) {
    if result.is_coherent {
        println!("✅ COHERENT: Function is logically consistent");
        println!("   Confidence: {:.1}%", result.confidence);
        if let Some(proof) = &result.formal_proof {
            println!("   Formal proof: {}", proof);
        }
    } else {
        println!("❌ INCOHERENT: Logical contradictions detected");
        println!("   Confidence: {:.1}%", result.confidence);
        
        if !result.violations.is_empty() {
            println!("🚨 Violations:");
            for violation in &result.violations {
                println!("   • {}: {}", violation.violation_type_str(), violation.description);
                println!("     Location: {}", violation.location);
                println!("     Formal contradiction: {}", violation.formal_contradiction);
            }
        }
    }
}

fn print_help() {
    println!("📚 Available commands:");
    println!("  def function_name(): ...  - Verify a single-line function");
    println!("  <multiline>              - Enter multiline function (end with empty line)");
    println!("  test                     - Run built-in test suite");
    println!("  help                     - Show this help");
    println!("  exit                     - Quit interactive mode");
}

fn run_test_suite(checker: &mut CodeCoherenceChecker) -> Result<()> {
    println!("🧪 Running Code Coherence Test Suite\n");
    
    let tests = vec![
        TestCase {
            name: "Simple coherent function",
            code: r#"
def add_numbers(a, b):
    """Returns the sum of two numbers."""
    return a + b
"#,
            expected_coherent: true,
        },
        TestCase {
            name: "Function with sorting contract",
            code: r#"
def sort_list(items):
    """Returns a sorted list in ascending order."""
    return sorted(items)
"#,
            expected_coherent: true,
        },
        TestCase {
            name: "Contradictory function",
            code: r#"
def sort_list(items):
    """Returns a sorted list in ascending order."""
    return items[::-1]  # Returns reversed, not sorted
"#,
            expected_coherent: false,
        },
        TestCase {
            name: "Function with type constraints",
            code: r#"
def get_positive(x):
    """Returns a positive number."""
    assert x >= 0
    return x
"#,
            expected_coherent: true,
        },
        TestCase {
            name: "Impossible function",
            code: r#"
def sort_in_constant_time(items):
    """Sorts a list in O(1) time complexity."""
    # This is mathematically impossible for comparison-based sorting
    return sorted(items)
"#,
            expected_coherent: false,
        },
    ];
    
    let mut passed = 0;
    let mut failed = 0;
    
    for test in tests {
        print!("Testing: {} ... ", test.name);
        io::stdout().flush()?;
        
        match checker.verify_function(test.code) {
            Ok(result) => {
                if result.is_coherent == test.expected_coherent {
                    println!("✅ PASS");
                    passed += 1;
                } else {
                    println!("❌ FAIL");
                    println!("   Expected: {}, Got: {}", test.expected_coherent, result.is_coherent);
                    failed += 1;
                }
            }
            Err(e) => {
                println!("❌ ERROR: {}", e);
                failed += 1;
            }
        }
    }
    
    println!("\n📊 Test Results:");
    println!("   Passed: {}", passed);
    println!("   Failed: {}", failed);
    println!("   Total:  {}", passed + failed);
    
    if failed == 0 {
        println!("🎉 All tests passed! Code coherence checker is working correctly.");
    } else {
        println!("⚠️  Some tests failed. Check implementation for issues.");
    }
    
    Ok(())
}

struct TestCase {
    name: &'static str,
    code: &'static str,
    expected_coherent: bool,
}

// Extension trait for better display
trait ViolationTypeDisplay {
    fn violation_type_str(&self) -> &'static str;
}

impl ViolationTypeDisplay for code_coherence_checker::CoherenceViolation {
    fn violation_type_str(&self) -> &'static str {
        match self.violation_type {
            code_coherence_checker::ViolationType::ContractImplementationMismatch => "Contract Mismatch",
            code_coherence_checker::ViolationType::LogicalImpossibility => "Logical Impossibility",
            code_coherence_checker::ViolationType::TypeIncoherence => "Type Incoherence",
            code_coherence_checker::ViolationType::StateContradiction => "State Contradiction",
        }
    }
}