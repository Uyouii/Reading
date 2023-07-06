## git

地址：https://learngitbranching.js.org/?locale=zh_CN

### git branch

 `git branch [name]`： 创建新分支

`git checkout [name]`: 切换到分支name

`git checkout -b <branch_name>`: 创建分支的同时切换分支

`git branch -d <branch>`: 删除本地分支

### 分支与合并

- `git merge`:在 Git 中合并两个分支时会产生一个特殊的提交记录，它有两个父节点。
  - 合并目标分支到当前分支：`git merge [branch_name]`
- `git rebase`: Rebase 实际上就是取出一系列的提交记录，“复制”它们，然后在另外一个地方逐个的放下去。
  - Rebase 的优势就是可以创造更线性的提交历史
  - `git rebase [branch_name]`：把当前分支rebase到目标分支


### 分离head

查看head指向：

1. `cat .git/HEAD`

2. `git symbolic-ref HEAD`

分离的 HEAD 就是让其指向了某个具体的提交记录而不是分支名。

`git checkout C1`：让HEAD指向提交记录C1

### 相对引用

可以使用`git log`查看提交记录的hash值

相对引用非常给力，两个简单的用法：

- 使用 `^` 向上移动 1 个提交记录
  - `git checkout main^`
  - 也可以将`HEAD`作为引用的参照：`git checkout HEAD^`
- 使用 `~<num>` 向上移动多个提交记录，如 `~3`

"~"操作符后面可以跟一个数字（可选，不跟数字时与 `^` 相同，向上移动一次），指定向上移动多少次。

例如后退4步：`git checkout HEAD~4`

可以直接使用-f让分支指向另一个提交：`git branch -f main HEAD~3`

### 撤销变更

主要有两种方法来撤销变更：

- `git reset`
  - `git reset`通过把分支记录回退几个提交记录来实现撤销改动。你可以将这想象成“改写历史”。`git reset` 向上移动分支，原来指向的提交记录就跟从来没有提交过一样。
  - 例如：`git reset HEAD~1`
  - 虽然在本地分支中使用 `git reset` 很方便，但是这种“改写历史”的方法对大家一起使用的远程分支是无效的。
- `git revert`:
  - 为了撤销更改并**分享**给别人，需要使用 `git revert`。
  - 例如：`git revert HEAD`
  - `git revert`会引用更改来撤销上一次的提交，因此会新创建一个版本。

### 整理提交记录

`git cherry-pick <提交号>...`: 将一些提交复制到当前所在的位置（`HEAD`）下面

e.g.： `git cherry-pick C2 C4`

### 交互式的rebase

交互式 rebase 指的是使用带参数 `--interactive` 的 rebase 命令, 简写为 `-i`

例如：`git rebase -i HEAD~4`

### 本地栈式提交

如果只想让git复制解决问题的那个提交记录，可以使用:

- `git rebase -i`
- `git cherry-pick`

来达到目的。

### Git Tags

Git tag可以（在某种程度上 —— 因为标签可以被删除后重新在另外一个位置创建同名的标签）永久地将某个特定的提交命名为里程碑，然后就可以像分支一样引用了。

更难得的是，它们并不会随着新的提交而移动。你也不能切换到某个标签上面进行修改提交，它就像是提交树上的一个锚点，标识了某个特定的位置。

`git tag v1 C1`:将这个标签命名为 `v1`，并且明确地让它指向提交记录 `C1`。如果不指定提交记录，Git 会用 `HEAD` 所指向的位置。

`git checkout v1`: 将head指向v1

### git describe

`git describe`: 标签在代码库中起着“锚点”的作用，Git 还为此专门设计了一个命令用来**描述**离你最近的锚点（也就是标签）。

`git describe` 的语法是：

```
git describe <ref>
```

`<ref>` 可以是任何能被 Git 识别成提交记录的引用，如果你没有指定的话，Git 会以你目前所检出的位置（`HEAD`）。

它输出的结果是这样的：

```
<tag>_<numCommits>_g<hash>
```

`tag` 表示的是离 `ref` 最近的标签， `numCommits` 是表示这个 `ref` 与 `tag` 相差有多少个提交记录， `hash` 表示的是你所给定的 `ref` 所表示的提交记录哈希值的前几位。

当 `ref` 提交记录上有某个标签时，则只输出标签名称

### 选择父提交记录

操作符 `^` 与 `~` 符一样，后面也可以跟一个数字。

但是该操作符后面的数字与 `~` 后面的不同，并不是用来指定向上返回几代，而是指定合并提交记录的某个父提交。Git 默认选择合并提交的“第一个”父提交，在操作符 `^` 后跟一个数字可以改变这一默认行为。

`git checkout main^2`

### 远程分支

检出远程分支：`git checkout origin/main`

远程分支有一个特别的属性，在你检出时自动进入分离 HEAD 状态。Git 这么做是出于不能直接在这些分支上进行操作的原因, 你必须在别的地方完成你的工作, （更新了远程分支之后）再用远程分享你的工作成果。

远程分支有一个命名规范 —— 它们的格式是: `<remote name>/<branch name>`

因此，如果你看到一个名为 `o/main` 的分支，那么这个分支就叫 `main`，远程仓库的名称就是 `o`。

大多数的开发人员会将它们主要的远程仓库命名为 `origin`，并不是 `o`。这是因为当你用 `git clone` 某个仓库时，Git 已经帮你把远程仓库的名称设置为 `origin` 了。

`git branch -vv`:查看本地分支和远程分支的对应属性

### git fetch

`git fetch`:从远程仓库获取数据

`git fetch` 完成了仅有的但是很重要的两步:

- 从远程仓库下载本地仓库中缺失的提交记录
- 更新远程分支指针(如 `o/main`)

`git fetch` 实际上将本地仓库中的远程分支更新成了远程仓库相应分支最新的状态。

`git fetch` 并不会改变你本地仓库的状态。它不会更新你的 `main` 分支，也不会修改你磁盘上的文件。

理解这一点很重要，因为许多开发人员误以为执行了 `git fetch` 以后，他们本地仓库就与远程仓库同步了。它可能已经将进行这一操作所需的所有数据都下载了下来，但是**并没有**修改你本地的文件。我们在后面的课程中将会讲解能完成该操作的命令 :D

所以, 你可以将 `git fetch` 的理解为单纯的下载操作。

### git pull

由于先抓取更新再合并到本地分支这个流程很常用，因此 Git 提供了一个专门的命令来完成这两个操作。它就是我们要讲的 `git pull`。

`git pull` 就是 git fetch 和 git merge 的缩写！

### git push

`git push` 负责将**你的**变更上传到指定的远程仓库，并在远程仓库上合并你的新提交记录。一旦 `git push` 完成, 你的朋友们就可以从这个远程仓库下载你分享的成果了！

`git push` 不带任何参数时的行为与 Git 的一个名为 `push.default` 的配置有关。它的默认值取决于你正使用的 Git 的版本。

（历史偏离）有许多的不确定性，Git 是不会允许你 `push` 变更的。实际上它会强制你先合并远程最新的代码，然后才能分享你的工作:

```sh
git fetch; 
git rebase o/main; 
git push
```

或者

```sh
git fetch;
git merge o/main
git push
```

`git pull --rebase`是fetch和rebase的简写。

```sh
git pull --rebase
git push
```

### rebase 和 merge

优点:

- Rebase 使你的提交树变得很干净, 所有的提交都在一条线上

缺点:

- Rebase 修改了提交树的历史

比如, 提交 C1 可以被 rebase 到 C3 之后。这看起来 C1 中的工作是在 C3 之后进行的，但实际上是在 C3 之前。

一些开发人员喜欢保留提交历史，因此更偏爱 merge。而其他人（比如我自己）可能更喜欢干净的提交树，于是偏爱 rebase。仁者见仁，智者见智。

### 远程分支跟踪

`main` 与 `o/main` 是相关的。这种关联在以下两种情况下可以清楚地得到展示：

- pull 操作时, 提交记录会被先下载到 o/main 上，之后再合并到本地的 main 分支。隐含的合并目标由这个关联确定的。
- push 操作时, 我们把工作从 `main` 推到远程仓库中的 `main` 分支(同时会更新远程分支 `o/main`) 。这个推送的目的地也是由这种关联确定的！

`main` 和 `o/main` 的关联关系就是由分支的“remote tracking”属性决定的。`main` 被设定为跟踪 `o/main` —— 这意味着为 `main` 分支指定了推送的目的地以及拉取后合并的目标。

当你克隆仓库的时候, Git 就自动帮你把这个属性设置好了。

当你克隆时, Git 会为远程仓库中的每个分支在本地仓库中创建一个远程分支（比如 `o/main`）。然后再创建一个跟踪远程仓库中活动分支的本地分支，默认情况下这个本地分支会被命名为 `main`。

克隆完成后，你会得到一个本地分支（如果没有这个本地分支的话，你的目录就是“空白”的），但是可以查看远程仓库中所有的分支（如果你好奇心很强的话）。这样做对于本地仓库和远程仓库来说，都是最佳选择。

这也解释了为什么会在克隆的时候会看到下面的输出：

```sh
local branch "main" set to track remote branch "o/main"
```

你可以让任意分支跟踪 `o/main`, 然后该分支会像 `main` 分支一样得到隐含的 push 目的地以及 merge 的目标。 这意味着你可以在分支 `totallyNotMain` 上执行 `git push`，将工作推送到远程仓库的 `main` 分支上。

有两种方法设置这个属性，第一种就是通过远程分支检出一个新的分支，执行: 

```sh
git checkout -b totallyNotMain o/main
```

就可以创建一个名为 `totallyNotMain` 的分支，它跟踪远程分支 `o/main`。

另一种设置远程追踪分支的方法就是使用：`git branch -u` 命令，执行：

```
git branch -u o/main foo
```

这样 `foo` 就会跟踪 `o/main` 了。如果当前就在 foo 分支上, 还可以省略 foo：

```
git branch -u o/main
```

### git push参数

我们可以为 push 指定参数，语法是：

```sh
git push <remote> <place>
```

```
git push origin main
```

把这个命令翻译过来就是：

*切到本地仓库中的“main”分支，获取所有的提交，再到远程仓库“origin”中找到“main”分支，将远程仓库中没有的提交记录都添加上去，搞定之后告诉我。*

我们通过“place”参数来告诉 Git 提交记录来自于 main, 要推送到远程仓库中的 main。它实际就是要同步的两个仓库的位置。

需要注意的是，因为我们通过指定参数告诉了 Git 所有它需要的信息, 所以它就忽略了我们所检出的分支的属性！

要同时为源和目的地指定 `<place>` 的话，只需要用冒号 `:` 将二者连起来就可以了：

```sh
git push origin <source>:<destination>
```

`source` 可以是任何 Git 能识别的位置：

例如：`git push origin foo^:main`

### git fetch参数

`git fetch` 的参数和 `git push` 极其相似。他们的概念是相同的，只是方向相反罢了。

```
git fetch <remote> <place>
```

如果你像如下命令这样为 git fetch 设置 的话：

```
git fetch origin foo
```

Git 会到远程仓库的 `foo` 分支上，然后获取所有本地不存在的提交，放到本地的 `o/foo` 上。

> 为何 Git 会将新提交放到 `o/foo` 而不是放到我本地的 foo 分支呢？之前不是说这样的 参数就是同时应用于本地和远程的位置吗？
>
>  本例中 Git 做了一些特殊处理，因为你可能在 foo 分支上的工作还未完成，你也不想弄乱它。还记得在 `git fetch` 课程里我们讲到的吗 —— 它不会更新你的本地的非远程分支, 只是下载提交记录（这样, 你就可以对远程分支进行检查或者合并了）。

如果指定 `<source>:<destination>` 会发生什么呢？

如果你觉得直接更新本地分支很爽，那你就用冒号分隔的 refspec 吧。不过，你不能在当前检出的分支上干这个事，但是其它分支是可以的。

这里有一点是需要注意的 —— `source` 现在指的是远程仓库中的位置，而 `<destination>` 才是要放置提交的本地仓库的位置。它与 git push 刚好相反，这是可以讲的通的，因为我们在往相反的方向传送数据。

理论上虽然行的通，但开发人员很少这么做。

Git 有两种关于 `<source>` 的用法是比较诡异的，即你可以在 git push 或 git fetch 时不指定任何 `source`，方法就是仅保留冒号和 destination 部分，source 部分留空。

- `git push origin :side`
- `git fetch origin :bugFix`

`git push origin :foo` ：我们通过给 push 传空值 source，成功删除了远程仓库中的 `foo` 分支, 这真有意思...

`git fetch origin :bar`：如果 fetch 空 到本地，会在本地创建一个新分支。

### git pull参数

git pull 到头来就是 fetch 后跟 merge 的缩写。你可以理解为用同样的参数执行 git fetch，然后再 merge 你所抓取到的提交记录。

以下命令在 Git 中是等效的:

`git pull origin foo` 相当于：

```sh
git fetch origin foo; git merge o/foo
```

还有...

`git pull origin bar~1:bugFix` 相当于：

```sh
git fetch origin bar~1:bugFix; git merge bugFix
```

例如：

`git pull origin main`:通过指定 `main` 我们更新了 `o/main`。然后将 `o/main` merge 到我们的检出位置，**无论**我们当前检出的位置是哪。

`git pull origin main:foo`:它先在本地创建了一个叫 `foo`的分支，从远程仓库中的 main 分支中下载提交记录，并合并到 `foo`，然后再 merge 到我们的当前检出的分支 `bar`上。

