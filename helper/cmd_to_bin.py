#!/usr/bin/env python
import sys
import re

CODE1 = {
  "add": "0000",
  "sub": "0001",
  "and": "0010",
  "or" : "0011",
  "xor": "0100",
  "cmp": "0101",
  "mov": "0110"
}

CODE2 = {  
  "sll": "1000",
  "slr": "1001",
  "srl": "1010",
  "sra": "1011",
}

CODE3 = {
  "ld": "00",
  "st": "01"
}

CODE4 = {
  "li": "000",
  "addi": "001",
  "b": "100",
}

CODE5 = {
  "be": "000",
  "blt": "001",
  "ble": "010",
  "bne": "011"
}

labels = {}

def dec_to_bin(x, dcount):
  xi = int(x)
  if xi >= 0:
    return bin(xi)[2:].zfill(dcount)
  else:
    return ('{:0' + str(dcount) + 'b}').format(xi & (2 ** (dcount) - 1))

def label_to_bin(label, dcount, here):
  if label.startswith(":"):
    return dec_to_bin(labels[label] - here - 1, dcount)
  else:
    return dec_to_bin(label, dcount)

print("WIDTH=16;\nDEPTH=4096;\nADDRESS_RADIX=UNS;\nDATA_RADIX=BIN;\nCONTENT BEGIN\n\t[0..4095] : 0;\n")

lines = [(i, line.strip()) for i, line in enumerate(sys.stdin)]

count = 0
for i, line in lines:
  if line.startswith("--"):
    continue
  if line.startswith(":"):
    assert line not in labels, "duplicate labels"
    labels[line] = count
    continue

  a = re.findall(r"[:-]?[\w']+", line)
  if len(a) >= 1 and ( a[0] in CODE1 or a[0] in CODE2 or a[0] == "in"  or
    a[0] == "out" or a[0] == "hlt" or a[0] == "nop" or a[0] == "bal" or a[0] == "bs" or
    a[0] in CODE3 or a[0] in CODE4 or a[0] in CODE5 ):
    count+=1

count = 0
for i, line in lines:
  if line.startswith("--"):
    print(line + " :" + str(i))
    continue

  if line.startswith(":"):
    print("--" + line)
    continue

  a = re.findall(r"[:-]?[\w']+", line)
  if not a:
    print("--")
    continue
  res = None

  try:
    if a[0] in CODE1:
      assert len(a) == 3, "unmatchd args"
      res = "11" + dec_to_bin(a[2], 3) + dec_to_bin(a[1], 3) + CODE1[a[0]] + "0000"
    if a[0] in CODE2:
      assert len(a) == 3, "unmatchd args"
      res = "11" + "000" + dec_to_bin(a[1], 3) + CODE2[a[0]] + dec_to_bin(a[2], 4)
    if a[0] == "in":
      res = "11" + "000" + dec_to_bin(a[1], 3) + "1100" + dec_to_bin(a[2], 4)
    if a[0] == "out":
      assert len(a) == 3, "unmatchd args"
      res = "11" + dec_to_bin(a[1], 3) + "000" + "1101" + dec_to_bin(a[2], 4)
    if a[0] == "hlt":
      assert len(a) == 1, "unmatchd args"
      res = ("1100000011110000");
    if a[0] == "nop":
      assert len(a) == 1, "unmatchd args"
      res = "1110000011101111";
    if a[0] in CODE3:
      assert len(a) == 4, "unmatchd args"
      res = CODE3[a[0]] + dec_to_bin(a[3], 3) + dec_to_bin(a[1], 3) + dec_to_bin(a[2], 8)
    if a[0] == "bal":
      res = "10110000" + label_to_bin(a[1], 8, count)
    if a[0] == "bs":
      res = "1010100000000000"
    if a[0] in CODE4:
      assert len(a) == 3, "unmatchd args"
      res = "10" + CODE4[a[0]] + dec_to_bin(a[1], 3) + label_to_bin(a[2], 8, count)
    if a[0] in CODE5:
      assert len(a) == 2, "unmatchd args"
      res = "10" + "111" + CODE5[a[0]] + label_to_bin(a[1], 8, count)

    assert res is not None, "may not be an inst!"
    assert len(res) == 16, res + "is an ilegal inst!"

    print("\t" + str(count) + ":\t" + res + "; -- " + line)
  except Exception as e:
    raise RuntimeError(str(i) + ": " + line + " -> " + e.args[0])

  count+=1

print("END;")
