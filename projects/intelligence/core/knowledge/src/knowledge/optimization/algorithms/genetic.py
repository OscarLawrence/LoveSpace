"""
Genetic algorithm optimization
"""

import asyncio
import random
from typing import Dict, Any, List

from ..data_models import OptimizationContext, OptimizationDecision


class GeneticOptimizer:
    """Genetic algorithm for exploration in uncertain environments"""
    
    def __init__(self):
        self.population_size = 20
        self.generations = 5
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7
    
    async def optimize(self, context: OptimizationContext,
                     analysis: Dict[str, Any]) -> OptimizationDecision:
        """Genetic algorithm optimization"""
        population = [self._generate_random_parameters() for _ in range(self.population_size)]
        
        for generation in range(self.generations):
            fitness_scores = [self._evaluate_fitness(individual, context) for individual in population]
            population = self._genetic_selection_reproduction(population, fitness_scores)
        
        final_fitness = [self._evaluate_fitness(individual, context) for individual in population]
        best_individual = population[final_fitness.index(max(final_fitness))]
        
        return OptimizationDecision(
            strategy_name="genetic_optimized",
            parameters=best_individual,
            expected_improvement=max(final_fitness),
            confidence=0.6,
            reasoning="Genetic algorithm exploration with population evolution",
            execution_time=0.0
        )
    
    def _generate_random_parameters(self) -> Dict[str, Any]:
        """Generate random parameter set"""
        return {
            "batch_size": random.randint(16, 128),
            "learning_rate": random.uniform(0.0001, 0.1),
            "threads": random.randint(1, 8),
            "cache_size": random.randint(256, 2048),
            "optimization_level": random.choice([1, 2, 3])
        }
    
    def _evaluate_fitness(self, individual: Dict[str, Any], context: OptimizationContext) -> float:
        """Evaluate fitness of individual"""
        if not context.historical_performance:
            return random.uniform(0.3, 0.7)
        
        historical_avg = sum(
            sum(perf.values()) / len(perf) for perf in context.historical_performance[-3:]
        ) / min(len(context.historical_performance), 3)
        
        parameter_score = 0.0
        for param, value in individual.items():
            if param == "batch_size" and 32 <= value <= 64:
                parameter_score += 0.1
            elif param == "learning_rate" and 0.001 <= value <= 0.01:
                parameter_score += 0.1
            elif param == "threads" and value >= 2:
                parameter_score += 0.05
        
        return historical_avg + parameter_score + random.uniform(-0.05, 0.05)
    
    def _genetic_selection_reproduction(self, population: List[Dict], fitness_scores: List[float]) -> List[Dict]:
        """Selection and reproduction with crossover and mutation"""
        new_population = []
        
        sorted_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)
        elite_size = max(2, self.population_size // 4)
        
        for i in range(elite_size):
            new_population.append(population[sorted_indices[i]].copy())
        
        while len(new_population) < self.population_size:
            parent1 = self._tournament_selection(population, fitness_scores)
            parent2 = self._tournament_selection(population, fitness_scores)
            
            if random.random() < self.crossover_rate:
                child = self._crossover(parent1, parent2)
            else:
                child = parent1.copy()
            
            if random.random() < self.mutation_rate:
                child = self._mutate(child)
            
            new_population.append(child)
        
        return new_population[:self.population_size]
    
    def _tournament_selection(self, population: List[Dict], fitness_scores: List[float]) -> Dict:
        """Tournament selection"""
        tournament_size = 3
        tournament_indices = random.sample(range(len(population)), tournament_size)
        best_index = max(tournament_indices, key=lambda i: fitness_scores[i])
        return population[best_index]
    
    def _crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        """Single-point crossover"""
        child = {}
        for key in parent1.keys():
            if random.random() < 0.5:
                child[key] = parent1[key]
            else:
                child[key] = parent2[key]
        return child
    
    def _mutate(self, individual: Dict) -> Dict:
        """Mutation operator"""
        mutated = individual.copy()
        
        for key, value in mutated.items():
            if random.random() < 0.3:  # 30% chance to mutate each parameter
                if key == "batch_size":
                    mutated[key] = max(16, min(128, value + random.randint(-16, 16)))
                elif key == "learning_rate":
                    mutated[key] = max(0.0001, min(0.1, value * random.uniform(0.5, 2.0)))
                elif key == "threads":
                    mutated[key] = max(1, min(8, value + random.randint(-2, 2)))
                elif key == "cache_size":
                    mutated[key] = max(256, min(2048, value + random.randint(-256, 256)))
        
        return mutated
