import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;

public class Main {

    private static final int DEPTH = 7;
    private static final int BRANCHING_FACTOR = 3;

    private static long minimaxVisitedNodes;
    private static long alphaBetaVisitedNodes;

    public static void main(String[] args) {

        Random random = new Random();

        Node root = generateTree(0, random);

        System.out.println("Tree parameters:");
        System.out.println("Depth: " + DEPTH);
        System.out.println("Branching factor: " + BRANCHING_FACTOR);
        System.out.println();

        /*
         * Ordinary minimax
         */
        minimaxVisitedNodes = 0;

        long start = System.nanoTime();

        int minimaxResult = minimax(root, DEPTH, true);

        long end = System.nanoTime();

        long minimaxTime = end - start;

        System.out.println("===== MINIMAX =====");
        System.out.println("Result: " + minimaxResult);
        System.out.println("Visited nodes: " + minimaxVisitedNodes);
        System.out.println("Time: " + minimaxTime + " ns");
        System.out.println();

        /*
         * Alpha-beta: natural order
         */
        alphaBetaVisitedNodes = 0;

        start = System.nanoTime();

        int alphaBetaNaturalResult = alphaBeta(
                root,
                DEPTH,
                Integer.MIN_VALUE,
                Integer.MAX_VALUE,
                true,
                false
        );

        end = System.nanoTime();

        long alphaBetaNaturalTime = end - start;

        System.out.println("===== ALPHA-BETA: NATURAL ORDER =====");
        System.out.println("Result: " + alphaBetaNaturalResult);
        System.out.println("Visited nodes: " + alphaBetaVisitedNodes);
        System.out.println("Time: " + alphaBetaNaturalTime + " ns");
        System.out.println();

        /*
         * Alpha-beta: reverse order
         */
        alphaBetaVisitedNodes = 0;

        start = System.nanoTime();

        int alphaBetaReverseResult = alphaBeta(
                root,
                DEPTH,
                Integer.MIN_VALUE,
                Integer.MAX_VALUE,
                true,
                true
        );

        end = System.nanoTime();

        long alphaBetaReverseTime = end - start;

        System.out.println("===== ALPHA-BETA: REVERSE ORDER =====");
        System.out.println("Result: " + alphaBetaReverseResult);
        System.out.println("Visited nodes: " + alphaBetaVisitedNodes);
        System.out.println("Time: " + alphaBetaReverseTime + " ns");
    }

    /**
     * Generates a complete tree.
     * Each internal node has 3 children.
     * Leaf values are random integers from -100 to 100.
     */
    private static Node generateTree(int currentDepth, Random random) {

        if (currentDepth == DEPTH) {
            return new Node(random.nextInt(201) - 100);
        }

        Node node = new Node();

        for (int i = 0; i < BRANCHING_FACTOR; i++) {
            node.children.add(generateTree(currentDepth + 1, random));
        }

        return node;
    }

    /**
     * Ordinary minimax algorithm.
     */
    private static int minimax(Node node, int depth, boolean maximizingPlayer) {

        minimaxVisitedNodes++;

        if (depth == 0 || node.isLeaf()) {
            return node.value;
        }

        if (maximizingPlayer) {

            int bestValue = Integer.MIN_VALUE;

            for (Node child : node.children) {
                int value = minimax(child, depth - 1, false);
                bestValue = Math.max(bestValue, value);
            }

            return bestValue;

        } else {

            int bestValue = Integer.MAX_VALUE;

            for (Node child : node.children) {
                int value = minimax(child, depth - 1, true);
                bestValue = Math.min(bestValue, value);
            }

            return bestValue;
        }
    }

    /**
     * Minimax with alpha-beta pruning.
     *
     * reverseOrder = false -> natural child order
     * reverseOrder = true  -> reverse child order
     */
    private static int alphaBeta(
            Node node,
            int depth,
            int alpha,
            int beta,
            boolean maximizingPlayer,
            boolean reverseOrder
    ) {

        alphaBetaVisitedNodes++;

        if (depth == 0 || node.isLeaf()) {
            return node.value;
        }

        List<Node> children = node.children;

        if (reverseOrder) {
            children = new ArrayList<>(node.children);
            Collections.reverse(children);
        }

        if (maximizingPlayer) {

            int bestValue = Integer.MIN_VALUE;

            for (Node child : children) {

                int value = alphaBeta(
                        child,
                        depth - 1,
                        alpha,
                        beta,
                        false,
                        reverseOrder
                );

                bestValue = Math.max(bestValue, value);

                alpha = Math.max(alpha, bestValue);

                if (beta <= alpha) {
                    break;
                }
            }

            return bestValue;

        } else {

            int bestValue = Integer.MAX_VALUE;

            for (Node child : children) {

                int value = alphaBeta(
                        child,
                        depth - 1,
                        alpha,
                        beta,
                        true,
                        reverseOrder
                );

                bestValue = Math.min(bestValue, value);

                beta = Math.min(beta, bestValue);

                if (beta <= alpha) {
                    break;
                }
            }

            return bestValue;
        }
    }

    static class Node {

        private int value;
        private final List<Node> children = new ArrayList<>();

        /**
         * Constructor for internal node.
         */
        public Node() {
        }

        /**
         * Constructor for leaf.
         */
        public Node(int value) {
            this.value = value;
        }

        public boolean isLeaf() {
            return children.isEmpty();
        }
    }
}