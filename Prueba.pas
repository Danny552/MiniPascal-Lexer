{ EJEMPLO DEL LIBRO PAG . 77}

program DemoPrimero; { cabecera }
{ Este es nuestro primer programa en Turbo Pascal }
uses Crt, DOS;  { declaraciones }
CONST
    Pi = 3.1416;
    IVA = 12;
    HEX = $FF;
    COMPLEX = 4.1E-1.3; 
type
    Palabra = string[20];
    Notas = 1..10;
var
    Salario : real;
    Numero  : integer;
    Apellido: Palabra;
    Pesos   : Notas;
begin
    ClrScr; { borra o limpia la pantalla }
    Write ('Cual es su primer apellido? ');
    ReadLn (Apellido);
    Writeln ('Escriba un numero Sr:', Apellido);
    ReadLn (Numero);
    Writeln ('El cuadrado del numero es: ', Numero*Numero);
    { fin del cuerpo del programa }
end.