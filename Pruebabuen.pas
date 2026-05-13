program TestGood;

var
    base, height, area: integer;
    i: integer;

begin
    base := 10;
    height := 20;
    
    { Testing a simple assignment }
    area := base + height;

    { Testing a loop }
    for i := 1 to 5 do
    begin
        area := area + 1;
        write(area);  { This semicolon is required by p_statement }
    end

    writeln('Success');
end.