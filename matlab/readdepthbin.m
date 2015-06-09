function r = readdepthbin(name,w,h)

fid = fopen(name,'rb');
r = fread(fid,[w,h],'int16');
r = r';
r(r == 0) = NaN;
r = r/65535;