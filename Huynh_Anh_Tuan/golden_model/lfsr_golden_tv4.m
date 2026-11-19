%% lfsr_golden_tv4.m - GOLDEN MODEL TV4 (Huynh Anh Tuan) - LFSR 8 bit, da thuc 1 + x + x^6 + x^7 + x^8
% Do an nhom: 8-bit TSPC LFSR BIST (gpdk090). Golden model cua TV4; scripts/gen_tb.py doc out/*.csv de sinh testbench.
% Chay: mo MATLAB -> cd vao thu muc chua file nay -> go  lfsr_golden_tv4
% Ket qua: thu muc out/ canh file nay
%   golden_lfsr_255.csv / .hex   bang 256 trang thai (chu ky 0..255) - Golden Reference Vector
%   golden_lfsr_300.csv          301 trang thai cho testbench 300 chu ky clock
%   golden_cfsr_256.csv          CFSR 257 trang thai (qua trang thai 00)
%   golden_lt_rtpg_k2.csv        LT-RTPG k = 2 (che do giam lat, LP = 1)
%   fault_dictionary.csv         chu ky MISR khi tiem loi SA0/SA1 o ngo ra CUT (tham khao TV5/TV6)
%   bao_cao_golden_matlab.txt    bao cao kiem chung toan hoc
%   hinh_*.png                   hinh cho bao cao (dang song Q[7:0], chuoi trang thai, Golomb, LT-RTPG)
% Phan cung: thanh ghi dich Q0 -> Q7, D0 = Q0 ^ Q5 ^ Q6 ^ Q7, seed 0x01 sau RST.
% Tuong thich MATLAB R2019b (khong dung ham moi hon).

clear; clc; close all;
here = fileparts(mfilename('fullpath'));
if isempty(here), here = pwd; end
outdir = fullfile(here, 'out');
if ~exist(outdir, 'dir'), mkdir(outdir); end

N    = 8;             % so bit
TAPS = [0 5 6 7];     % vi tri tap hoi tiep (Q0, Q5, Q6, Q7)
SEED = 1;             % 0x01
NCYC = 300;           % so canh clock cua testbench (ke hoach nhom: 300 chu ky)

fid = fopen(fullfile(outdir, 'bao_cao_golden_matlab.txt'), 'w');
P = @(varargin) both(fid, varargin{:});
P('GOLDEN MODEL TV4 (MATLAB %s) - LFSR 8 bit, P(x) = 1 + x + x^6 + x^7 + x^8\n', version('-release'));
P('Hoi tiep: D0 = Q0 ^ Q5 ^ Q6 ^ Q7, dich Q0 -> Q7, seed = 0x%02X\n', SEED);
P('%s\n', repmat('=', 1, 72));

%% 1. Chuoi trang thai LFSR
S = zeros(NCYC + 1, 1);            % S(t+1) = trang thai sau t canh clock
S(1) = SEED;
for t = 1:NCYC
    S(t + 1) = lfsr_step(S(t), TAPS, N, false);
end
per   = find(S(2:end) == SEED, 1);
nuniq = numel(unique(S(1:255)));
P('1. Chu ky LFSR tu seed 0x%02X: %d (ly thuyet 2^8 - 1 = 255)\n', SEED, per);
P('   So trang thai khac nhau trong 255 chu ky: %d ; co trang thai 00: %d\n', nuniq, any(S(1:255) == 0));
P('   11 trang thai dau: %s\n', strjoin(cellstr(dec2hex(S(1:11), 2))', ' '));
P('   Trang thai sau 255 canh = 0x%02X (quay ve seed: %d)\n\n', S(256), S(256) == SEED);

%% 2. Kiem chung dai so: ma tran dong hanh T tren GF(2), Q(t+1) = T*Q(t) mod 2
T = zeros(N);
T(1, TAPS + 1) = 1;                % Q0(t+1) = XOR cac tap
for i = 2:N
    T(i, i - 1) = 1;               % Q_i(t+1) = Q_(i-1)(t)
end
okT = true;                        % T khop voi mo phong tung buoc
for t = 1:255
    okT = okT && isequal(mod(T * bits(S(t), N), 2), bits(S(t + 1), N));
end
I8 = eye(N);
e255 = isequal(gf2pow(T, 255), I8);
others = [85 51 15];               % 255/3, 255/5, 255/17
eo = arrayfun(@(e) isequal(gf2pow(T, e), I8), others);
P('2. Ma tran dong hanh T (Q(t+1) = T.Q(t) mod 2), khop mo phong 255 buoc: %d\n', okT);
for i = 1:N
    P('      %s\n', sprintf('%d ', T(i, :)));
end
P('   T^255 = I: %d ; T^85 = I: %d ; T^51 = I: %d ; T^15 = I: %d\n', e255, eo);
prim = e255 && ~any(eo);
P('   => bac cua T = 255 = 2^8 - 1 (255 = 3.5.17): da thuc dac trung NGUYEN THUY: %d\n', prim);
P('   Da thuc dac trung cua T: x^8 + x^7 + x^2 + x + 1 (doi xung cua P(x), cung nguyen thuy)\n\n');

%% 3. CFSR (them NOR(Q0..Q6) - mach CFSR_FB cua TV3) - 256 trang thai
C = zeros(258, 1);                 % bat dau tu 0x00 (reset), 258 trang thai de thay doan 80 -> 00 -> 01
for t = 1:257
    C(t + 1) = lfsr_step(C(t), TAPS, N, true);
end
perC = find(C(2:end) == 0, 1);
k80  = find(C(1:256) == hex2dec('80'), 1);
P('3. CFSR tu 0x00: chu ky %d, so trang thai khac nhau %d (ly thuyet 256)\n', perC, numel(unique(C(1:256))));
P('   Doan qua trang thai 0: %s -> %s -> %s\n\n', dec2hex(C(k80), 2), dec2hex(C(k80 + 1), 2), dec2hex(C(k80 + 2), 2));

%% 4. Tinh ngau nhien - 3 tien de Golomb tren dong bit Q7 (255 chu ky)
b  = bitget(S(1:255), N);          % Q7
L  = numel(b);
[rl, rv] = run_lengths(b);
P('4. Golomb tren dong bit Q7, 255 chu ky\n');
P('   (1) Can bang: %d so 1, %d so 0 (ly thuyet 128 / 127)\n', sum(b), L - sum(b));
P('   (2) Tong so run: %d (ly thuyet 128)\n', numel(rl));
for len = 1:8
    P('       dai %d: %3d run so 1, %3d run so 0\n', len, sum(rl == len & rv == 1), sum(rl == len & rv == 0));
end
x  = 1 - 2 * b;                    % 0 -> +1, 1 -> -1
R  = zeros(L, 1);
for tau = 0:L - 1
    R(tau + 1) = sum(x .* circshift(x, -tau));
end
P('   (3) Tu tuong quan: R(0) = %d ; R(1..254) chi nhan gia tri %s\n\n', R(1), mat2str(unique(R(2:end))'));

%% 5. LT-RTPG (che do giam lat) - Wang & Gupta TCAD 2006
base  = S(1:256);
tg0   = toggles(base);
P('5. LT-RTPG (LP = 1), 255 chu ky, 8 ngo ra den CUT\n');
P('   LFSR thuong (LP = 0): %.3f bit lat/chu ky, %d vector khac nhau\n', mean(tg0), numel(unique(base(1:255))));
Vk = cell(1, 3);
for k = [2 3]
    V = lt_rtpg(S, k, N);
    Vk{k} = V;
    tg = toggles(V(1:256));
    P('   LT k=%d: %.3f bit lat/chu ky (giam %.1f%%), %d vector khac nhau, phu A[3:0] %d/16, B[3:0] %d/16\n', ...
      k, mean(tg), 100 * (1 - sum(tg) / sum(tg0)), numel(unique(V(1:255))), ...
      numel(unique(bitand(V(1:255), 15))), numel(unique(bitshift(V(1:255), -4))));
end
P('   Chon phan cung LT_RTPG_8bit: k = 2 (cap Q_i, Q_i+1), T-FF reset ve 0.\n\n');

%% 6. MISR + CUT cong 4 bit (THAM KHAO cho TV5/TV6 - cau truc that do TV5 chot)
P('6. MISR 8 bit (cung da thuc, S(t+1) = step(S) ^ Z, reset 0x00), CUT = cong 4 bit A = V[3:0], B = V[7:4]\n');
fnames = {'S0', 'S1', 'S2', 'S3', 'Cout'};
fd = fopen(fullfile(outdir, 'fault_dictionary.csv'), 'w');
fprintf(fd, 'che_do,loi,chu_ky_hex,ket_qua\n');
modes = {'LP0', base(2:256); 'LP1_LT_k2', Vk{2}(2:256)};
for m = 1:2
    vec  = modes{m, 2};
    good = misr_sig(cut_adder4(vec), TAPS, N);
    fprintf(fd, '%s,fault_free,%02X,\n', modes{m, 1}, good);
    det = 0;
    for i = 0:4
        for sv = 0:1
            z = cut_adder4(vec);
            z = bitset(z, i + 1, sv);
            sig = misr_sig(z, TAPS, N);
            det = det + (sig ~= good);
            res = 'PHAT HIEN'; if sig == good, res = 'ALIASING'; end
            fprintf(fd, '%s,%s_SA%d,%02X,%s\n', modes{m, 1}, fnames{i + 1}, sv, sig, res);
        end
    end
    P('   %-10s chu ky dung 0x%02X ; phat hien %d/10 loi SA0/SA1 o ngo ra CUT\n', modes{m, 1}, good, det);
end
fclose(fd);
P('   Nhan xet: chay dung 255 chu ky thi SA0 va SA1 tren cung mot day cho CUNG chu ky (I + T + ... + T^254 = 0\n');
P('   khi T^255 = I): van phat hien loi nhung khong phan biet SA0/SA1; muon chan doan thi chay so chu ky khac 255.\n\n');

%% 7. Ghi bang vector chuan
f1 = fopen(fullfile(outdir, 'golden_lfsr_255.csv'), 'w');
f2 = fopen(fullfile(outdir, 'golden_lfsr_255.hex'), 'w');
fprintf(f1, 'cycle,hex,Q7..Q0,Q0,Q1,Q2,Q3,Q4,Q5,Q6,Q7,D0_next\n');
for t = 0:255
    s = S(t + 1); q = bits(s, N)';
    fprintf(f1, '%d,%02X,%s,%s,%d\n', t, s, dec2bin(s, N), strjoin(arrayfun(@num2str, q, 'UniformOutput', false), ','), ...
            mod(sum(q(TAPS + 1)), 2));
    fprintf(f2, '%02X\n', s);
end
fclose(f1); fclose(f2);
f1 = fopen(fullfile(outdir, 'golden_lfsr_300.csv'), 'w');
fprintf(f1, 'cycle,hex,Q7..Q0\n');
for t = 0:NCYC
    fprintf(f1, '%d,%02X,%s\n', t, S(t + 1), dec2bin(S(t + 1), N));
end
fclose(f1);
f1 = fopen(fullfile(outdir, 'golden_cfsr_256.csv'), 'w');
fprintf(f1, 'cycle,hex,Q7..Q0\n');
for t = 0:256
    fprintf(f1, '%d,%02X,%s\n', t, C(t + 1), dec2bin(C(t + 1), N));
end
fclose(f1);
f1 = fopen(fullfile(outdir, 'golden_lt_rtpg_k2.csv'), 'w');
fprintf(f1, 'cycle,Q_hex,V_hex(LP=1),bit_lat_V\n');
V2 = Vk{2};
for t = 0:255
    tl = 0; if t > 0, tl = sum(bits(bitxor(V2(t + 1), V2(t)), N)); end
    fprintf(f1, '%d,%02X,%02X,%d\n', t, S(t + 1), V2(t + 1), tl);
end
fclose(f1);

%% 8. Hinh cho bao cao
% 8.1 Dang song Q[7:0] 40 chu ky dau
f = figure('Name', 'Dang song Q[7:0]', 'Position', [80 80 1000 560], 'Color', 'w');
nshow = 40; tt = 0:nshow;
hold on;
for i = 0:N - 1
    y = bitget(S(1:nshow + 1), i + 1);
    stairs(tt, y * 0.8 + 1.2 * i, 'LineWidth', 1.4);
end
set(gca, 'YTick', (0:N - 1) * 1.2 + 0.4, 'YTickLabel', arrayfun(@(i) sprintf('Q%d', i), 0:N - 1, 'UniformOutput', false));
xlabel('Chu ky clock'); title('Golden model: dang song Q[7:0] (seed 0x01, 40 chu ky dau)');
xlim([0 nshow]); ylim([-0.3 1.2 * N]); grid on; box on;
for t = 0:5:nshow
    text(t + 0.1, 1.2 * N - 0.15, dec2hex(S(t + 1), 2), 'FontSize', 8, 'Color', [0.4 0.4 0.4]);
end
print(f, fullfile(outdir, 'hinh_dang_song_Q.png'), '-dpng', '-r150');

% 8.2 Chuoi trang thai va ban do tra ve S(t) -> S(t+1)
f = figure('Name', 'Chuoi trang thai', 'Position', [100 100 1100 420], 'Color', 'w');
subplot(1, 2, 1);
stairs(0:NCYC, S, 'LineWidth', 1); hold on;
plot([255 255], [0 255], 'r--'); xlim([0 NCYC]); ylim([0 256]);
xlabel('Chu ky'); ylabel('Gia tri Q[7:0]'); title('Chuoi 300 chu ky, lap lai sau 255 (vach do)'); grid on;
subplot(1, 2, 2);
plot(S(1:255), S(2:256), '.', 'MarkerSize', 10);
xlabel('S(t)'); ylabel('S(t+1)'); title('Ban do S(t) -> S(t+1): 255 diem, khong co 0');
axis([0 255 0 255]); axis square; grid on;
print(f, fullfile(outdir, 'hinh_chuoi_trang_thai.png'), '-dpng', '-r150');

% 8.3 Golomb: phan bo run va tu tuong quan
f = figure('Name', 'Golomb', 'Position', [120 120 1100 420], 'Color', 'w');
subplot(1, 2, 1);
cnt = zeros(8, 2);
for len = 1:8
    cnt(len, :) = [sum(rl == len & rv == 0), sum(rl == len & rv == 1)];
end
bar(1:8, cnt); legend('run so 0', 'run so 1'); xlabel('Do dai run'); ylabel('So run');
title('Phan bo run (Q7, 255 chu ky)'); grid on;
subplot(1, 2, 2);
stem(0:L - 1, R, 'filled', 'MarkerSize', 3);
xlabel('\tau'); ylabel('R(\tau)'); title('Tu tuong quan: R(0) = 255, R(\tau \neq 0) = -1');
xlim([0 L - 1]); grid on;
print(f, fullfile(outdir, 'hinh_golomb.png'), '-dpng', '-r150');

% 8.4 LT-RTPG: so bit lat moi chu ky
f = figure('Name', 'LT-RTPG', 'Position', [140 140 1000 420], 'Color', 'w');
subplot(1, 2, 1);
plot(1:255, tg0, '-', 1:255, toggles(Vk{2}(1:256)), '-', 'LineWidth', 1);
legend('LFSR (LP = 0)', 'LT-RTPG k = 2 (LP = 1)'); xlabel('Chu ky'); ylabel('So bit lat'); grid on;
title('So bit lat o ngo vao CUT moi chu ky');
subplot(1, 2, 2);
m = [mean(tg0), mean(toggles(Vk{2}(1:256))), mean(toggles(Vk{3}(1:256)))];
bar(m); set(gca, 'XTickLabel', {'LFSR', 'LT k=2', 'LT k=3'});
ylabel('Bit lat trung binh / chu ky'); grid on;
for i = 1:3, text(i - 0.15, m(i) + 0.1, sprintf('%.2f', m(i))); end
title('Giam 50% (k = 2) va 75% (k = 3)');
print(f, fullfile(outdir, 'hinh_lt_rtpg.png'), '-dpng', '-r150');

P('\nKET LUAN: chu ky 255 = %d, nguyen thuy = %d, Golomb (can bang 128/127) = %d, CFSR 256 = %d\n', ...
  per == 255, prim, sum(b) == 128, perC == 256);
P('File ket qua: thu muc out/ canh file lfsr_golden_tv4.m\n');
fclose(fid);

%% ===================== HAM CUC BO =====================
function both(fid, varargin)
    fprintf(varargin{:});
    fprintf(fid, varargin{:});
end

function s = lfsr_step(s, taps, n, cfsr)
    % Dich trai 1 bit (Q0 -> Q1 ... Q6 -> Q7), D0 = XOR cac tap [+ NOR(Q0..Q6) neu CFSR]
    f = 0;
    for t = taps
        f = bitxor(f, bitget(s, t + 1));
    end
    if cfsr && bitand(s, 127) == 0
        f = bitxor(f, 1);
    end
    s = bitor(bitand(bitshift(s, 1), 2^n - 1), f);
end

function q = bits(s, n)
    % cot [Q0; Q1; ...; Q(n-1)]
    q = double(bitget(s, 1:n))';
end

function M = gf2pow(A, e)
    % A^e tren GF(2) (binh phuong va nhan)
    M = eye(size(A));
    B = A;
    while e > 0
        if mod(e, 2), M = mod(M * B, 2); end
        B = mod(B * B, 2);
        e = floor(e / 2);
    end
end

function [len, val] = run_lengths(b)
    % Run tuan hoan: xoay de bat dau tai cho doi bit dau tien
    b = b(:);
    k = find(b ~= circshift(b, 1), 1);
    b = circshift(b, -(k - 1));
    edges = [1; find(diff(b) ~= 0) + 1; numel(b) + 1];
    len = diff(edges);
    val = b(edges(1:end - 1));
end

function tg = toggles(seq)
    tg = zeros(numel(seq) - 1, 1);
    for i = 1:numel(seq) - 1
        tg(i) = sum(bitget(bitxor(seq(i), seq(i + 1)), 1:8));
    end
end

function V = lt_rtpg(Q, k, n)
    % T-FF moi bit: v_i(t+1) = v_i(t) ^ AND(Q_i, ..., Q_(i+k-1)) (chi so mod n), v(0) = 0, ngo ra V(t) = v(t)
    V = zeros(size(Q));
    v = 0;
    for t = 1:numel(Q)
        V(t) = v;
        a = 0;
        for i = 0:n - 1
            x = 1;
            for j = 0:k - 1
                x = x * bitget(Q(t), mod(i + j, n) + 1);
            end
            a = bitor(a, x * 2^i);
        end
        v = bitxor(v, a);
    end
end

function z = cut_adder4(v)
    % CUT mac dinh: cong 4 bit, A = V[3:0], B = V[7:4], Cin = 0 -> Z = {Cout, S3..S0}
    z = mod(bitand(v, 15) + bitshift(v, -4), 32);
end

function s = misr_sig(z, taps, n)
    s = 0;
    for t = 1:numel(z)
        s = bitxor(lfsr_step(s, taps, n, false), z(t));
    end
end
