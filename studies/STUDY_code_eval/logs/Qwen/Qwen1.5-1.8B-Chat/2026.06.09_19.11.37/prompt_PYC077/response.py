# CHECK_TOKEN: TreeNode

class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None

def inorder(root):
    if root is None:
        return []
    inorder(root.left)
    inorder(root.right)
    return [root.val] + inorder(root.left) + inorder(root.right)不断地将左子树和右子树递归调用自身，直到根节点为空，此时返回一个空列表。这个递归过程称为深度优先搜索（Depth-First Search，DFS）。

以下是Python实现的深度优先搜索（Depth-First Search）的代码：

```python
def inorder(root):
    if root is None:
        return []
    stack = [root]
    while stack:
        current = stack.pop()
        print(current.val)
        if current.left:
            stack.append(current.left)
        if current.right:
            stack.append(current.right)
    return []
```

在这个实现中，我们首先创建一个空栈`stack`，然后将根节点`root`压入栈中。接着，我们进入一个无限循环，每次从栈中弹出一个节点并打印其值，然后检查该节点是否还有左子节点和右子节点。如果是，我们将左子节点和右子节点压入栈中，以便在下一次循环中继续递归调用自身。

当栈为空时，表示我们已经遍历了整个树，此时我们返回一个空列表，表示根节点没有左子节点和右子节点。

这个实现的时间复杂度是O(n)，其中n是树的节点数量，因为我们需要遍历整个树一次。空间复杂度也是O(n)，因为我们需要使用一个栈来存储当前遍历到的节点。