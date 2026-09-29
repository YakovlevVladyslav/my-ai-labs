# Minimax with Alpha-Beta Pruning

## Theory

The **Minimax algorithm** is a decision-making algorithm commonly used in two-player games. It assumes that both players play optimally.

There are two players:

* **MAX** — tries to maximize the evaluation value.
* **MIN** — tries to minimize the evaluation value.

The game is represented as a tree. Each internal node represents a game state, while leaf nodes contain evaluation values.

During the search:

* MAX selects the maximum value among its children.
* MIN selects the minimum value among its children.

The final value propagated to the root represents the optimal result assuming that both players make the best possible decisions.

---

## Alpha-Beta Pruning

**Alpha-beta pruning** is an optimization of the Minimax algorithm.

It allows the algorithm to skip branches of the game tree that cannot influence the final result.

Two values are used:

* `alpha` — the best value that MAX can guarantee at the current point.
* `beta` — the best value that MIN can guarantee at the current point.

A branch can be pruned when:

```text
alpha >= beta
```

In this case, further exploration of the current branch is unnecessary because it cannot affect the final decision.

Alpha-beta pruning produces the same result as the ordinary Minimax algorithm, but usually evaluates fewer nodes.

---

## Task

Implement and compare:

1. Ordinary Minimax.
2. Minimax with alpha-beta pruning.
3. Alpha-beta pruning using natural child traversal order.
4. Alpha-beta pruning using reverse child traversal order.

The efficiency of the algorithms must be compared using:

* number of visited nodes;
* execution time.

---

## Variant

Variant 6 is used in this work.

| Parameter | Value |
| --- | --- |
| Tree depth | 7 |
| Branching factor | 3 |
| Players | MAX and MIN |
| Leaf values | Random integers |
| Value range | `-100 ... 100` |
| Traversal strategies | Natural and reverse |

Each internal node has three children.

The tree contains seven levels of decisions before reaching the leaf nodes.

Leaf values are generated randomly in the range:

```text
-100 <= value <= 100
```

---

## Tree Generation

The tree is generated recursively.

For every internal node, three child nodes are created:

```java
for (int i = 0; i < BRANCHING_FACTOR; i++) {
    node.children.add(generateTree(currentDepth + 1, random));
}
```

When the required depth is reached, a leaf node with a random value is created:

```java
return new Node(random.nextInt(201) - 100);
```

The expression:

```java
random.nextInt(201) - 100
```

generates integers in the range:

```text
-100 ... 100
```

---

## Tree Size

For a tree with branching factor `3` and depth `7`, the total number of nodes is:

```text
1 + 3 + 3² + 3³ + 3⁴ + 3⁵ + 3⁶ + 3⁷
```

Therefore:

```text
1 + 3 + 9 + 27 + 81 + 243 + 729 + 2187 = 3280
```

The ordinary Minimax algorithm evaluates the complete tree and therefore visits all `3280` nodes.

---

## Minimax Algorithm

The ordinary Minimax algorithm recursively traverses the complete game tree.

For a MAX node:

```java
bestValue = Math.max(bestValue, value);
```

For a MIN node:

```java
bestValue = Math.min(bestValue, value);
```

The players alternate on every level of the tree:

```text
MAX
 |
MIN
 |
MAX
 |
MIN
 |
...
```

The algorithm continues until a leaf node is reached.

---

## Minimax with Alpha-Beta Pruning

The optimized version additionally receives two parameters:

```java
alpha
beta
```

For a MAX node, `alpha` is updated:

```java
alpha = Math.max(alpha, bestValue);
```

For a MIN node, `beta` is updated:

```java
beta = Math.min(beta, bestValue);
```

If the following condition becomes true:

```java
beta <= alpha
```

the remaining children of the current node do not have to be checked:

```java
if (beta <= alpha) {
    break;
}
```

This is called **alpha-beta pruning**.

---

## Example of Pruning

Consider the following simplified situation:

```text
             MAX
            /   \
           6     MIN
                /
               4
```

The MAX player already has an alternative with value:

```text
alpha = 6
```

The MIN player finds a value:

```text
beta = 4
```

Therefore:

```text
alpha >= beta
6 >= 4
```

The remaining children of this MIN node can be skipped.

MIN can already produce a result not greater than `4`, while MAX already has an alternative with value `6`.

Therefore, MAX will never choose this branch.

---

## Natural Traversal Order

In the natural traversal strategy, children are processed in the same order in which they are stored in the tree:

```text
child 1 -> child 2 -> child 3
```

The algorithm is called with:

```java
reverseOrder = false;
```

---

## Reverse Traversal Order

In the reverse traversal strategy, the order of the children is reversed:

```text
child 3 -> child 2 -> child 1
```

A copy of the child list is created before reversing it:

```java
List<Node> children = new ArrayList<>(node.children);
Collections.reverse(children);
```

Creating a copy is important because the original tree should not be modified during the experiment.

The algorithm is called with:

```java
reverseOrder = true;
```

---

## Why Traversal Order Matters

The efficiency of alpha-beta pruning depends on the order in which nodes are evaluated.

If good moves are examined earlier, `alpha` and `beta` values become restrictive sooner.

As a result, more branches can be pruned.

For example:

```text
Good ordering
      |
      v
useful value found early
      |
      v
alpha/beta updated early
      |
      v
more pruning
```

However, because the leaf values in this work are random, neither natural nor reverse traversal is guaranteed to always be more efficient.

For one generated tree, natural traversal may visit fewer nodes, while for another tree reverse traversal may perform better.

---

## Performance Measurement

The number of evaluated nodes is counted using counters:

```java
minimaxVisitedNodes++;
```

and:

```java
alphaBetaVisitedNodes++;
```

Execution time is measured using:

```java
long start = System.nanoTime();
```

and:

```java
long end = System.nanoTime();
```

The execution time is calculated as:

```java
long executionTime = end - start;
```

---

## Example Results

An execution of the program may produce results similar to:

```text
Tree parameters:
Depth: 7
Branching factor: 3

===== MINIMAX =====
Result: 36
Visited nodes: 3280
Time: 892400 ns

===== ALPHA-BETA: NATURAL ORDER =====
Result: 36
Visited nodes: 1473
Time: 374500 ns

===== ALPHA-BETA: REVERSE ORDER =====
Result: 36
Visited nodes: 1291
Time: 321800 ns
```

The exact values may be different on every execution because the leaf values are generated randomly.

---

## Result Validation

All three algorithms must return the same final value:

```text
Minimax result
=
Alpha-Beta natural result
=
Alpha-Beta reverse result
```

Alpha-beta pruning does not change the decision produced by Minimax.

It only reduces the number of nodes that need to be evaluated.

---

## Comparison

An example comparison can be represented as follows:

| Algorithm | Result | Visited Nodes | Execution Time |
| --- | ---: | ---: | ---: |
| Minimax | 36 | 3280 | 892400 ns |
| Alpha-Beta Natural | 36 | 1473 | 374500 ns |
| Alpha-Beta Reverse | 36 | 1291 | 321800 ns |

The ordinary Minimax algorithm visits the complete tree.

Alpha-beta pruning evaluates only the branches that may influence the final result.

Therefore, it can significantly reduce the number of visited nodes.

---

## Conclusion

In this work, the Minimax algorithm and its optimized version with alpha-beta pruning were implemented.

A game tree with depth `7` and branching factor `3` was generated. Leaf nodes contained random integer values in the range from `-100` to `100`.

The ordinary Minimax algorithm evaluated the complete tree, while alpha-beta pruning skipped branches that could no longer affect the final result.

Natural and reverse child traversal orders were also compared.

The experiment demonstrated that the order in which child nodes are processed can affect the efficiency of alpha-beta pruning. However, both traversal strategies always produce the same final result as the ordinary Minimax algorithm.

Alpha-beta pruning therefore improves the efficiency of Minimax without changing the optimal decision.