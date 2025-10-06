import os
import argparse
from ani_cluster.utils import setup_logging
from ani_cluster.determine_threshold import determine_threshold
from ani_cluster.get_representatives import get_representatives

def main():
        parser = argparse.ArgumentParser(description="Dereplicate genomes or determine optimal ANI threshold using fastANI output")
        subparsers = parser.add_subparsers(dest="mode", required=True)
        # --- Mode 1: determine_thresholds ---
        det_parser = subparsers.add_parser("determine_threshold", help="Determine the best ANI threshold by plotting thresholds vs number of clusters.")
        det_parser.add_argument("-a", "--ani", required=True, help="all-vs-all fastANI output TSV file.")
        det_parser.add_argument("-o", "--output", default="thresholds_vs_clusters.html", help="Output plot file name (default: thresholds_vs_clusters.html).")
        det_parser.add_argument("-t", "--thresholds", nargs=3, type=float, metavar=('START', 'END', 'STEP'), required=True, help="Range of ANI thresholds to test: START END STEP (e.g. 90 99 0.5)")

        # --- Mode 2: get_representatives ---
        rep_parser = subparsers.add_parser("get_representatives", help="Get dereplicated representative genomes (medoids)")
        rep_parser.add_argument("-a", "--ani", required=True, help="all-vs-all fastANI output TSV file.")
        rep_parser.add_argument("-t", "--threshold", type=float, required=True, help="ANI threshold for clustering")
        rep_parser.add_argument("-o", "--output", required=True, help="Output file for representative (medoid) genome list.")
        rep_parser.add_argument("-c", "--cluster_membership", help="Cluster membership file (Optional).")

        args = parser.parse_args()

        # Initialize logging
        try:
                output_dir = os.path.dirname(args.output) if os.path.dirname(args.output) else "."
                logger = setup_logging(output_dir, "ani_cluster.log")
                logger.info(f"Starting ANI clustering script in mode: {args.mode}.")
        except Exception as e:
                print(f"[FATAL] Failed to setup logging: {e}", file=sys.stderr)
                sys.exit(1)
        try:
                if args.mode == "determine_threshold":
                        start, end, step = args.thresholds
                        logger.info(f"Running threshold analysis from {start} to {end} with step {step}.")
                        determine_threshold(args.ani, args.output, start, end, step, logger)
                        logger.info(f"Threshold analysis complete. Plot saved to {args.output}")
                        sys.exit(0)

                elif args.mode == "get_representatives":
                        logger.info(f"Performing dereplication with ANI threshold {args.threshold}.")
                        medoids, clusters = get_representatives(args.ani, args.threshold, args.output, args.cluster_membership, logger)
                        logger.info(f"Found {len(clusters)} clusters. Representative genomes (medoids) from each are written to: {args.output}")
                        if args.cluster_membership:
                                logger.info(f"Cluster membership saved to: {args.cluster_membership}")
                        sys.exit(0)

                else:
                        parser.print_help()
                        sys.exit(1)
        except FileNotFoundError as e:
                logger.error(f"File not found: {e}")
                sys.exit(1)
        except ValueError as e:
                logger.error(f"Value error: {e}")
                sys.exit(1)
        except RuntimeError as e:
                logger.error(f"Runtime error: {e}")
                sys.exit(1)
        except KeyboardInterrupt:
                logger.error("Execution interrupted by user (Ctrl + C)")
                sys.exit(130)
        except Exception as e:
                logger.error(f"Unexpected error occured: {e}")
                sys.exit(1)
        finally:
                logger.info("Script finished.")

if __name__ == "__main__":
        main()
