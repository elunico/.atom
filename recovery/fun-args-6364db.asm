.macro push(%r)
	addi $sp $sp -4 	# make space for register
	sw %r, 0($sp)		# store register on stack
.end_macro

.macro pushi(%r)
	li $a0 %r
	push($a0)
	.end_macro

.macro pop(%r)
	lw %r ($sp) 		# load data from top of the stack
	addi $sp $sp 4		# move stack pointer down
.end_macro

.macro ret()
jr $ra
pop($a0)
.end_macro

.macro call(%r)
jal %r
.end_macro

.text


main:

  pushi(30)
  pushi(30)
  call(add) # return value in $a0
  li $v0 1 # print int
  syscall

  li $v0 10
  syscall


add:
  pop($t0)  # get arg1
  pop($t1)  # get arg2
  add $t2 $t0 $t1 # add the arguments
  push($t1) # push return value
  ret()     # return

.data
