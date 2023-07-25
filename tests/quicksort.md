> Some of the jars were broken, but I still had enough good ones for all my spices. Pretty labels and jars.
> It looks nice , the only thing the I wasn't happy about it that the stickers are not laminated.
> The product dimensions are wrong in the description. It says 1.4 inches wide and it is more like 1.69
> It’s 23 for 26$ not worth I will return it rather just buy some other ones
> Clean. Very nice to look at. I love it!!
> Completely reorganized the spice cupboard. These jars and labels were easy to use and fill. Still going strong after several months of use.
> Sturdy and well made
> Horrible. Just horrible.
call Quicksort *
# Quicksort
pop pivot
iterate arg
    > pivot
    call More-Positive?
    if-goto is-less
        <more>
        > x
        </more>
        next
    ## is-less
        <less>
        > x
        </less>
        next

<less>
call Quicksort *
</less>
iterate less
    pop x
    > x
    next

> pivot

<more>
call Quicksort *
</more>
iterate more
    pop x
    > x
    next

return

# More-Positive?
pop x
pop pivot
> x
<comparison>
> Review A:
> a
> Review B:
> b
> Is review A more positive than review B? (yes or no)
bool-reduce *
pop is-more
</comparison>
> is-more
return
