module controller(
  input clock, reset, exec,
  input [15:0] instr,
  
  output RegWrite, MemtoReg, RegDst, ALUSrc, PCSrc
  );
  
  wire [1:0] op1 = instr[15:14];
  wire [2:0] op2 = instr[13:11];
  wire [3:0] op3 = instr[7:4];
  
  assign RegWrite = (instr != 16'd0) && (
        (op1 == 2'b00 /* LD */)
    || ((op1 == 2'b11) && ~( /* Except */
           op3 == 4'b0101 /* CMP */
        || op3 == 4'b1101 /* OUT */
        || op3 == 4'b1111 /* HLT */))
    ||  (op1 == 2'b10 && op2 == 3'b000 /* LI */));
        
  assign MemtoReg = (op1 == 2'b00 /* LD */) || (op1 == 2'b11 && op3 == 4'b1100 /* IN */);
      
  assign RegDst = (op1 != 2'b00); /* Except LD */
  
  assign ALUSrc = (op3[3:2] == 2'b10);
  
  assign PCSrc = (op1 == 2'b10 && op2 == 3'b100)
              || (op1 == 2'b10 && instr[13:11] == 3'b111);

endmodule
