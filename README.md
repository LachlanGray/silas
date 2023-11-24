# Silas
This is something I made during the summer and forgot to share. It's a prototype programming language for controlled language model reasoning. It's a stack based programming language that involves storing, loading, manipulating, extending blocks of text.

The program syntax is consistent with markdown, and it is more or less a stack-based programming language, though this prototype is basic, and not super well thought out. As I write this readme it has been a few months since thinking about this.

You can define functions, push lines of text, fill text, and describe program flow based on generated content.
1) New lines of text are pushed with a markdown quote `> `, these get added to the bottom of the current block.
2) You can open a new block with `<blockname>` and close it again later with `</blockname>`. The current block is essentially context for the language model, and you can think of it like a page of text. Each block is a stack that grows line by line downards, and you are always inside of a block. You can also open blocks from within blocks. If a block already exists, opening it will open to the state of that block. If it doesn't exist, an empty block is created.
3) You can fill a variable called `name` by putting `[name]` in a pushed line. You can define stopping criteria with vertical bars like `[name|.]` which will terminate the generation when a period is produced.
4) You can use curly braces like `{name}` to insert the current value of the variable to a line.
5) You can define functions with a markdown header `# Name`. When you call a function, it takes the entire state of the current block as an argument.
6) For loops consume lines from the current block one by one.

Below is an example program that pushes a bunch of amazon reviews for spice jars, and asseses their positivity. The program calls a function called `Rate` that creates a block called reviews. Each iteration of the for loop starts a new block, prompts the language model to rate the review inside it, then adds the rating to the reviews block. 

The program is done executing when `return` is reached in the main body, and the state of the current block is returned. In this example, the program finishes with the `<reviews>` block still open, so this program returns the `<reviews>` block, containing a list of x/10 ratings.

You can run this example by doing
```
python silas.py -d examples/rate_reviews.md
```
(-d stands for debug and displays variable and block states during execution)

***

> Some of the jars were broken, but there were still enough
> It looks nice, although the stickers are not laminated.
> The product dimensions are wrong in the description.
> It’s 23 for 26$ not worth I will return it.
> Clean. Very nice to look at. I love it!!
> Completely reorganized the spice cupboard. Nice.
> Sturdy and well made
> Horrible. Just horrible.
call Rate *
return

# Rate
<reviews>
for review in arg
        > A user left the following review for a spice jar
        > "{review}"
        > Overall, its positivity on a scale of 1-10 is: [rating|*.|*\n]
    <reviews>
        > {rating}/10
    </reviews>
endfor
return

