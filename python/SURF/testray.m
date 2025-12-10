jsonFileName = '/Users/ben/Desktop/astramiz/python/SURF/3_30_2008_29555.json';
jsonData = readdictionary(jsonFileName);

z = jsonData('z');
z = z{:};
z = [z{:}];

p = jsonData('p');
p = p{:};
p = [p{:}];

s = jsonData('s');
s = s{:};
s = [s{:}];

t = jsonData{'t'};
t = t(:);
t = [t{:}];

c = 1449.2 + 4.6.*t - 0.055.*(t.^2) + 0.0029.*(t.^3) + (1.34 -0.01.*t).*(s-35) + 0.016.*z;

[x z t d] = raytrace(1,1,-5,5,z,c,true);