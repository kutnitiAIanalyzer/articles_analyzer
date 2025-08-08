import argparse
import os
import json
import logging

from llama_cpp import Llama

from config import DATA_DIR, TREATED_FILE, MODEL_PATH, QUESTION_TREE_PATH, LOG_LEVEL

from loaders.FileLoader import FileLoader
from processors.ArticleProcessor import ArticleProcessor
from evaluators.ArticleEvaluator import ArticleEvaluator

from analyzers.ExpertAnalyzer import ExpertAnalyzer
from analyzers.NaiveAnalyzer import NaiveAnalyzer
from analyzers.CompositeAnalyzer import CompositeAnalyzer
from analyzers.RelevanceAnalyzer import RelevanceAnalyzer
from analyzers.QuestionnaryAnalyzer import QuestionnaryAnalyzer

# Descriptions of each analyzer for CLI documentation
ANALYZER_DOCS = {
    "questionnary": "Decision tree-based analyzer using yes/no LLM answers at each node.",
    "expert": "Simulates a neutral media analyst specialized in Indian geopolitics.",
    "naive": "Simulates a thoughtful, open-minded person with no strong opinion about India.",
    "relevance": "Focuses solely on relevance estimation, ignoring sentiment or position.",
    "composite": "Combines multiple analyzers (e.g., expert + naive) to aggregate decisions."
}


def main():
    """Main entry point for the article classification pipeline."""

    # Set up logging based on LOG_LEVEL from .env
    logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO))

    # CLI arguments
    parser = argparse.ArgumentParser(description="Article classification using LLM-based analyzers.")
    parser.add_argument("--data-dir", type=str, default=DATA_DIR, help="Directory containing article .txt files and index.csv")
    parser.add_argument("--treated-file", type=str, default=TREATED_FILE, help="Path to treated articles JSON file")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of articles to process")
    parser.add_argument("--evaluate", action="store_true", help="Evaluate results using labels from index.csv")
    parser.add_argument("--fresh-start", action="store_true", help="Delete treated file and start fresh")
    parser.add_argument("--model-path", type=str, default=MODEL_PATH, help="Path to LLaMA model in GGUF format")
    parser.add_argument("--tree-path", type=str, default=QUESTION_TREE_PATH, help="Path to decision tree JSON file")
    parser.add_argument("--analyzer", type=str, choices=list(ANALYZER_DOCS.keys()), default="questionnary", help="Which analyzer to use for classification")
    parser.add_argument("--analyzer-help", type=str, nargs="?", const="all", help="Show explanation of available analyzers (or a specific one) and exit")
    args = parser.parse_args()

    # Show analyzer documentation if requested
    if args.analyzer_help:
        if args.analyzer_help == "all":
            print("[Available analyzers]:")
            for name, desc in ANALYZER_DOCS.items():
                print(f"- {name}: {desc}")
        else:
            desc = ANALYZER_DOCS.get(args.analyzer_help)
            if desc:
                print(f"[Analyzer: {args.analyzer_help}]\n{desc}")
            else:
                print(f"[ERROR] Unknown analyzer '{args.analyzer_help}'")
                print("Use --analyzer-help all to list all available analyzers.")
        return

    # Load the LLaMA model
    llm = Llama(
        model_path=args.model_path,
        n_ctx=4096,
        n_threads=12,
        n_gpu_layers=-1,
        verbose=False,
        logits_all=False,
        embedding=False,
        temperature=0.1,
        top_p=0.95,
        repeat_penalty=1.1,
        stop=["</s>"],
        max_tokens=500,
    )

    # Optionally start from scratch by deleting treated file
    if args.fresh_start:
        logging.info("Fresh start enabled. Deleting treated file.")
        try:
            os.remove(args.treated_file)
        except FileNotFoundError:
            logging.warning("Treated file %s not found. Skipping deletion.", args.treated_file)

    # Initialize the loader
    loader = FileLoader(data_dir=args.data_dir, treated_file=args.treated_file)

    # Instantiate the selected analyzer
    if args.analyzer == "questionnary":
        with open(args.tree_path, "r", encoding="utf-8") as f:
            tree_data = json.load(f)
        analyzer = QuestionnaryAnalyzer.build_tree_from_json(tree_data, llm)
    elif args.analyzer == "expert":
        analyzer = ExpertAnalyzer(llm)
    elif args.analyzer == "naive":
        analyzer = NaiveAnalyzer(llm)
    elif args.analyzer == "relevance":
        analyzer = RelevanceAnalyzer(llm)
    elif args.analyzer == "composite":
        analyzer = CompositeAnalyzer([ExpertAnalyzer(llm), NaiveAnalyzer(llm)])
    else:
        raise ValueError(f"Unsupported analyzer type: {args.analyzer}")

    # Process articles
    processor = ArticleProcessor(loader, analyzer)

    try:
        processor.run(limit=args.limit)
    except KeyboardInterrupt:
        logging.warning("Keyboard interrupt received. Proceeding to evaluation...")

    # Evaluate the output if requested or if results exist
    if args.evaluate or processor.results:
        evaluator = ArticleEvaluator(processor.results)
        evaluator.evaluate_binary_relevance()


if __name__ == "__main__":
    main()
