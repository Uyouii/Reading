## Effective Go

### Formatting

 The `gofmt` program (also available as `go fmt`, which operates at the package level rather than source file level) reads a Go program and emits the source in a standard style of indentation and vertical alignment, retaining and if necessary reformatting comments. 

Some formatting details remain. Very briefly:

- Indentation
  - We use tabs for indentation and `gofmt` emits them by default. Use spaces only if you must.
- Line length
  - Go has no line length limit. If a line feels too long, wrap it and indent with an extra tab.
- Parentheses（圆括号）
  - Go needs fewer parentheses than C and Java: control structures (`if`, `for`, `switch`) do not have parentheses in their syntax. Also, the operator precedence hierarchy is shorter and clearer, so
  - ```go
  x<<8 + y<<16
    ```
   means what the spacing implies, unlike in the other languages.

### Commentary（注释）

Go provides C-style `/* */` block comments and C++-style `//` line comments.

 Comments that appear before top-level declarations, with no intervening newlines, are extracted along with the declaration to serve as explanatory text for the item. The nature and style of these comments determine the quality of the documentation `godoc` produces.

Every package should have a *package comment*, a block comment preceding the package clause. For multi-file packages, the package comment only needs to be present in one file, and any one will do. 

The package comment should introduce the package and provide information relevant to the package as a whole. It will appear first on the `godoc` page and should set up the detailed documentation that follows.

Depending on the context, `godoc` might not even reformat comments. 

Inside a package, any comment immediately preceding a top-level declaration serves as a *doc comment* for that declaration. Every exported (capitalized) name in a program should have a doc comment.

If every doc comment begins with the name of the item it describes, you can use the [doc](https://go.dev/cmd/go/#hdr-Show_documentation_for_package_or_symbol) subcommand of the [go](https://go.dev/cmd/go/) tool and run the output through `grep`.

```shell
$ go doc -all regexp | grep -i parse
```

