program SemanticTest;
const
  MAX = 100;

var
 MAX: Integer;        { Error: Redeclaration of constant as variable }
  i: Integer;
  r: Real;
  arr: array[1..3] of Real;

procedure CheckVar(x: Real);
begin
  x := x + 1.0;
end;

begin
  MAX := 200;           { Error: Assignment to constant }
  i := 5.5;             { Error: Type mismatch (Real to Integer) }
  
  for i := 1 to 10 do
    i := i + 1;         { Error: Modification of loop control variable }

  CheckVar(10.5);
end.