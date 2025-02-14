# LC3 State Machine in Python

This is an implementation of the state machine as described in the book 

**Introduction to Computing Systems: from bits and gates to C/CC++ and beyond** by Patt and Patel.   


Especially **Appendix C: The Microarchitecture of the LC-3**.

The python implements the state machine as closely to the description as possible.   
It doesn't include trap instructions, not PSR processing.    

## Test program

Used here: https://wchargin.com/lc3web/

```
.orig x3000
   ; r0 to have address of mem2
   lea r0, mem2

   ; set mem3 to point to mem2
   ; to be
   ; mem3
   ;    .fill x3032
   st  r0, mem3

   ; swap two words at mem1
   ; so they end up as 
   ; mem1
   ;    .fill x4321
   ;    .fill x1234
   lea r0, mem1
   ldr r1, r0, #0
   ldr r2, r0, #1
   str r2, r0, #0
   str r1, r0, #1

   ; put r2 into address 
   ; stored in mem3 ie mem2
   ; mem2
   ;    .fill x4321
   sti r2, mem3

   ; should load r2 with 
   ; same value x4321
   ld  r2, mem2

   ; load r3 with second word at mem1
   ; x1234
   ldr r3, r0, #1

   ; skip next instruction
   br  lbl1
   and r0, r0, #0
lbl1
   lea r4, mem1
   ; set r5 to 5
   and r5, r5, #0
   add r5, r5, #5
   ; add to r5 then and with x0f
   ; should become x0009
   add r3, r3, r5 
   and r3, r3, x0f

   ; skip next instruction
   brp lbl2
   and r0, r0, #0
lbl2
   ldi r0, mem3
   not r4, r0
lbl3
   add r3, r3, #-1
   brp lbl3

   jsr sub1
   lea r6, sub2
   jsrr r6

spin
   br  spin

sub1
   add r0, r0, #1
   ret

sub2
   add r0, r0, #1
   ret

   ; should end up with registers
   ; as below
   ; R0: x4323   R1: x1234
   ; R2: x4321   R3: x0000
   ; R4: xBCDE   R5: x0005
   ; R6: x301D   R7: x301A
   ; PC: x301a

   ; space for extra instructions
   .blkw #17

mem1 
   .fill x1234
   .fill x4321
mem2
   .fill xabcd
mem3
   .fill xdcba
.end
```

## Good links

Datapath   
https://cs2461-2020.github.io/lectures/Datapath.pdf

https://lumetta.web.engr.illinois.edu/120-S19/slide-copies/134-hardwired-control-unit-design.pdf

https://lumetta.web.engr.illinois.edu/120-S19/
https://lumetta.web.engr.illinois.edu/120-S19/slide-copies/131-lc-3-control-signals.pdf
https://lumetta.web.engr.illinois.edu/120-S19/slide-copies/132-lc-3-fetch-control-signals.pdf
https://lumetta.web.engr.illinois.edu/120-S19/slide-copies/136-patt-and-patel-control-unit.pdf

### Example answers
https://users.ece.utexas.edu/~patt/13f.306/Exams/f13_final_soln.pdf


### LC3b

https://users.ece.utexas.edu/~patt/05f.360N/handouts/360n.appC.pdf

### Architecture

https://www.cs.utexas.edu/~fussell/courses/cs310h/handouts/handouts.shtml

https://www.cs.utexas.edu/~fussell/courses/cs310h/lectures/Lecture_10-310h.pdf

https://acg.cis.upenn.edu/milom/cse240-Fall05/
https://acg.cis.upenn.edu/milom/cse240-Fall05/handouts/Ch04.pdf
https://acg.cis.upenn.edu/milom/cse240-Fall05/handouts/Ch05.pdf

### McGraw Hill resources
Useful pages on race condition avoidance
p90 p134

https://icourse.club/uploads/files/96a2b94d4be48285f2605d843a1e6db37da9a944.pdf
https://highered.mheducation.com/sites/0072467509/student_view0/source_code.html

### Simulator
https://acg.cis.upenn.edu/milom/cse240-Fall05/handouts/lc3manual.html

### Cheat sheet
https://lumetta.web.engr.illinois.edu/120-S19/info/ECE120-S19-ZJUI-final-ref-sheets.pdf

### Design to implementation
https://coertvonk.com/inquiries/how-cpu-work/design-30973
https://coertvonk.com/inquiries/how-cpu-work/instruction-set-30971
https://coertvonk.com/inquiries/how-cpu-work/design-30973
https://coertvonk.com/inquiries/how-cpu-work/implementation-30975

https://winniewjeng.github.io/organization%20&%20programming/2020/06/09/Instruction-Set-Architecture/
https://winniewjeng.github.io/organization%20&%20programming/2020/06/08/LC3/
https://winniewjeng.github.io/organization%20&%20programming/2020/06/08/LC3-Registers/
https://winniewjeng.github.io/organization%20&%20programming/2020/06/08/LC3-Machine-Instruction/

### Virtual machine
**C**
https://www.jmeiners.com/lc3-vm/

**Rust**
https://www.rodrigoaraujo.me/posts/lets-build-an-lc-3-virtual-machine/

**Go**
https://github.com/jotingen/go-lc3?tab=readme-ov-file

https://github.com/Bl41r/lc-3-virtual-machine
https://github.com/paul-nameless/lc3-vm/blob/master/vm.py

**Jupyter VM
**https://github.com/Calysto/calysto_lc3/tree/master

### Assembler
https://github.com/paul-nameless/lc3-asm
https://github.com/pepaslabs/lc3as.py

### LC3 tools
https://github.com/haplesshero13/lc3tools
https://github.com/chiragsakhuja/lc3tools
https://www.cs.colostate.edu/~cs270/.Spring13/Recitations/R7/Recitation7.pdf

### LC3 and FSM VHDL
https://github.com/Sacusa/LC-3

### LC3uArch
https://sourceforge.net/projects/lc3uarch/

### Examples
https://people.cs.georgetown.edu/~squier/Teaching/HardwareFundamentals/LC3-trunk/docs/LC3-uArch-MemMapIOstacksINT.pdf
