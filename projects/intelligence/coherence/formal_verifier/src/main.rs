/*!
Formal Coherence Verifier CLI

Command-line interface for the Z3-based coherence checker.
Provides mathematical proofs of logical consistency.
*/

use clap::{Parser, Subcommand};
use coherence_verifier::{CoherenceVerifier, Statement, parse_statement};
use z3::{Config, Context};
use std::io::{self, Write};

#[derive(Parser)]
#[command(name = "coherence")]
#[command(about = "Formal coherence verification using Z3 theorem prover")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Verify consistency of statements
    Verify {
        /// Statements to verify (can be repeated)
        #[arg(short, long, action = clap::ArgAction::Append)]
        statement: Vec<String>,
    },
    /// Check if conclusion follows from premises
    Reasoning {
        /// Premise statements
        #[arg(short, long, action = clap::ArgAction::Append)]
        premise: Vec<String>,
        /// Conclusion statement
        #[arg(short, long)]
        conclusion: String,
    },
    /// Interactive mode
    Interactive,
    /// Test with built-in examples
    Test,
}

fn main() -> anyhow::Result<()> {
    let cli = Cli::parse();

    let cfg = Config::new();
    let ctx = Context::new(&cfg);
    let mut verifier = CoherenceVerifier::new(&ctx);

    match cli.command {
        Commands::Verify { statement } => {
            verify_statements(&mut verifier, &statement)?;
        }
        Commands::Reasoning { premise, conclusion } => {
            verify_reasoning(&mut verifier, &premise, &conclusion)?;
        }
        Commands::Interactive => {
            run_interactive(&mut verifier)?;
        }
        Commands::Test => {
            run_tests(&mut verifier)?;
        }
    }

    Ok(())
}

fn verify_statements(verifier: &mut CoherenceVerifier, statements: &[String]) -> anyhow::Result<()> {
    if statements.is_empty() {
        println!("No statements provided");
        return Ok(());
    }

    println!("🔍 Formal Coherence Verification");
    println!("================================");
    
    let parsed_statements: Vec<Statement> = statements
        .iter()
        .enumerate()
        .map(|(i, text)| parse_statement(text, &format!("stmt_{}", i)))
        .collect();

    for (i, stmt) in parsed_statements.iter().enumerate() {
        println!("{}. {}", i + 1, stmt.text);
        if !stmt.predicates.is_empty() {
            println!("   Predicates: {:?}", stmt.predicates);
        }
    }
    println!();

    let result = verifier.verify_statements(&parsed_statements)?;

    if result.is_consistent {
        println!("✅ CONSISTENT: Statements are logically consistent");
        if let Some(proof) = result.proof {
            println!("   Proof: {}", proof);
        }
        println!("   Confidence: {:.1}%", result.confidence * 100.0);
    } else {
        println!("❌ INCONSISTENT: Logical contradictions detected");
        if let Some(proof) = result.proof {
            println!("   Proof: {}", proof);
        }
        
        if !result.contradictions.is_empty() {
            println!("\n🚨 Contradictions:");
            for contradiction in &result.contradictions {
                println!("   • {} ↔ {}", contradiction.statement1, contradiction.statement2);
                println!("     Reason: {}", contradiction.reason);
                println!("     Formal: {}", contradiction.formal_proof);
            }
        }
        println!("   Confidence: {:.1}%", result.confidence * 100.0);
    }

    Ok(())
}

fn verify_reasoning(verifier: &mut CoherenceVerifier, premises: &[String], conclusion: &str) -> anyhow::Result<()> {
    println!("🔗 Formal Reasoning Verification");
    println!("===============================");
    
    let premise_statements: Vec<Statement> = premises
        .iter()
        .enumerate()
        .map(|(i, text)| parse_statement(text, &format!("premise_{}", i)))
        .collect();
    
    let conclusion_statement = parse_statement(conclusion, "conclusion");

    println!("Premises:");
    for (i, premise) in premise_statements.iter().enumerate() {
        println!("  {}. {}", i + 1, premise.text);
    }
    println!("Conclusion:");
    println!("  → {}", conclusion_statement.text);
    println!();

    let result = verifier.verify_reasoning_chain(&premise_statements, &conclusion_statement)?;

    if result.is_consistent {
        println!("✅ VALID: Conclusion logically follows from premises");
        if let Some(proof) = result.proof {
            println!("   Proof: {}", proof);
        }
    } else {
        println!("❌ INVALID: Conclusion does not follow from premises");
        if let Some(proof) = result.proof {
            println!("   Proof: {}", proof);
        }
    }
    println!("   Confidence: {:.1}%", result.confidence * 100.0);

    Ok(())
}

fn run_interactive(verifier: &mut CoherenceVerifier) -> anyhow::Result<()> {
    println!("🔍 Interactive Formal Coherence Verifier");
    println!("========================================");
    println!("Commands:");
    println!("  verify <statement1> | <statement2> | ... - Verify consistency");
    println!("  reason <premise1> | <premise2> | ... → <conclusion> - Check reasoning");
    println!("  test - Run built-in tests");
    println!("  quit - Exit");
    println!();

    loop {
        print!("> ");
        io::stdout().flush()?;
        
        let mut input = String::new();
        io::stdin().read_line(&mut input)?;
        let input = input.trim();

        if input.is_empty() {
            continue;
        }

        if input == "quit" || input == "exit" {
            break;
        }

        if input == "test" {
            run_tests(verifier)?;
            continue;
        }

        if input.starts_with("verify ") {
            let statements_text = &input[7..];
            let statements: Vec<String> = statements_text
                .split(" | ")
                .map(|s| s.trim().to_string())
                .collect();
            verify_statements(verifier, &statements)?;
        } else if input.contains(" → ") {
            let parts: Vec<&str> = input.split(" → ").collect();
            if parts.len() == 2 {
                let premises_text = parts[0].trim();
                let conclusion = parts[1].trim().to_string();
                
                let premises: Vec<String> = if premises_text.starts_with("reason ") {
                    premises_text[7..]
                        .split(" | ")
                        .map(|s| s.trim().to_string())
                        .collect()
                } else {
                    premises_text
                        .split(" | ")
                        .map(|s| s.trim().to_string())
                        .collect()
                };
                
                verify_reasoning(verifier, &premises, &conclusion)?;
            } else {
                println!("Invalid format. Use: <premise1> | <premise2> → <conclusion>");
            }
        } else {
            println!("Unknown command. Type 'quit' to exit.");
        }
        
        println!();
    }

    Ok(())
}

fn run_tests(verifier: &mut CoherenceVerifier) -> anyhow::Result<()> {
    println!("🧪 Running Built-in Tests");
    println!("=========================");

    // Test 1: Obvious contradiction
    println!("\nTest 1: Obvious Contradiction");
    let statements = vec![
        "All AI systems are perfectly logical".to_string(),
        "Current AI systems contain contradictions".to_string(),
    ];
    verify_statements(verifier, &statements)?;

    // Test 2: Consistent statements
    println!("\nTest 2: Consistent Statements");
    let statements = vec![
        "Some AI systems are logical".to_string(),
        "Some AI systems contain errors".to_string(),
    ];
    verify_statements(verifier, &statements)?;

    // Test 3: Invalid reasoning
    println!("\nTest 3: Invalid Reasoning");
    let premises = vec![
        "All AI systems are perfectly logical".to_string(),
        "Current AI systems contain contradictions".to_string(),
    ];
    let conclusion = "Therefore, no AI systems exist".to_string();
    verify_reasoning(verifier, &premises, &conclusion)?;

    // Test 4: Valid reasoning (simplified)
    println!("\nTest 4: Valid Reasoning");
    let premises = vec![
        "We need coherent tools".to_string(),
        "Coherent tools require validation".to_string(),
    ];
    let conclusion = "We need validation".to_string();
    verify_reasoning(verifier, &premises, &conclusion)?;

    println!("\n✅ Tests completed");
    Ok(())
}