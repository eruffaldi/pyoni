
syms fx1 fy1 cx1 cy1 real
syms fx2 fy2 cx2 cy2 real
syms p1x p1y p1z real
syms p1_ix p1_iy  real

divw = @(p) p./p(4);
divz = @(p) p./p(3);

p1 = [p1x p1y p1z 1]'; % world coordinate

K1 = [fx1 0 cx1; 0 fy1 cy1; 0 0 1];
K2 = [fx2 0 cx2; 0 fy2 cy2; 0 0 1];
K1_44 = blkdiag(K1,1);
K2_44 = blkdiag(K2,1);
P = [1 0 0 0; 0 1 0 0; 0 0 0 1; 0 0 1 0];
iP = inv(P);


% image point from local
p1i_3 = divz(K1_44*p1)
p1i_4 = divw(P*K1_44*p1)
p1h_3 = K1_44*p1;
p1h_4 = K1_44*p1;

% second image  point from local, without the [R|t]
p1_i4 = [p1_ix p1_iy 1.0/p1z 1]'; 
p1_h4 = p1_i4/p1_i4(3); % p1_h4 = p1_i4*p1_i4.z so we c
p2_h4 = P*K2_44*inv(K1_44)*inv(P)*p1_h4;
p2_i4 = divw(p2_h4)
