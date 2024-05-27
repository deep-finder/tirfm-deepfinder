close all;
clear all;

%prefix = '/net/serpico-fs2/emoebel/';
prefix = '/Users/amasson/Remotes/serpico-fs2/emoebel/';

addpath([prefix, 'tools/matlab/mytools/motl_tools']);

% path_atlas_segmaps = [prefix, 'tirfm_exocytose/paper/data/atlas/segmentations_h5/'];
path_atlas_segmaps = ['/Users/amasson/Documents/tirfm_exocytose/', 'segmentations_h5/'];

listing = dir(path_atlas_segmaps);

path_dset = [prefix, 'tirfm_exocytose/paper/data/for_deepfinder/dataset/'];

output_path = '/Users/amasson/Documents/tirfm_exocytose/segmentations_merged_h5_matlab/';

if (~exist(output_path, 'dir')); mkdir(output_path); end%if

% for IDX=3:60
for IDX=3:4
    folder_name = listing(IDX).name;
    display([num2str(IDX), ' ============= ', num2str(folder_name), ' ....']);
    
    %folder_name = strrep(folder_name, ' ', '\ ');  % handle blank spaces
    
    motl_exo = objlist2motl([path_dset, folder_name, '/objl.xml']);
    
    seg = h5read([path_atlas_segmaps, folder_name, '/segmap_atlas.h5'], '/dataset');
    seg = int8(seg);
    
    % this operation is needed to get correct orientation:
    %seg = permute(seg, [2 1 3]);
    
    %--------------------------------------------------------------------------
    % Get 3D CC, and erase CCs that correspond to annotated exo spots:
    CC3d = bwconncomp(seg);
    target = seg;
    
    S = regionprops(CC3d,'Centroid');
    N  = numel(S);
    
    motl = zeros(20,N);
    for idx=1:N
        motl(6 ,idx) = idx;
        motl(7 ,idx) = numel(CC3d.PixelIdxList{idx});
        motl(8 ,idx) = S(idx).Centroid(2);
        motl(9 ,idx) = S(idx).Centroid(1);
        motl(10,idx) = S(idx).Centroid(3);
    end
    
    D = motl_compare(motl_exo, motl, 5);
    vect_corresp = sum(D,1); % only considered as TP if =1
    idx_corresp = find(vect_corresp==1);
    
    % Erase all spots that correspond to exocytosis:
    for ii=1:numel(idx_corresp)
        % Get pixel list of spot:
        spot_idx = idx_corresp(ii);
        PixelIdxList = CC3d.PixelIdxList{spot_idx};
        % Erase pixel from segm map:
        for jj=1:numel(PixelIdxList)
            target(PixelIdxList(jj)) = 0;
        end
    end
    
    %--------------------------------------------------------------------------
    % Now get 2D CC to get coordinates of "normal" spots. We use 2D CC because
    % the spot detector (Atlas) operates in 2D
    
    motl_normal = [];
    for s=1:size(target,3)
        CC2d = bwconncomp(target(:,:,s));
        S = regionprops(CC2d,'Centroid');
        N = numel(S);
        %display(['Slice ', num2str(s), 'nb of spots: ', num2str(N)]);
        for idx=1:N
            m = zeros(20,1);
            m(6) = idx;
            m(7) = numel(CC2d.PixelIdxList{idx});
            m(8) = S(idx).Centroid(2);
            m(9) = S(idx).Centroid(1);
            m(10) = s;
            
            motl_normal = [motl_normal m];
        end
    end
    
    %--------------------------------------------------------------------------
    % Fuse object lists and seg target:
    
    N = 9800; % motl_normal is way too big (~70k) therefore subsample
    idx_rnd = randperm(size(motl_normal,2));
    idx_rnd = idx_rnd(1:N);
    motl_normal = motl_normal(:,idx_rnd);

    % motl_normal = motl_normal(:,1:N);
    
    motl_normal(20,:) = 1; % 'normal' spot is class1;
    motl_exo(20,:) = 2; % 'exo' spot is class2;
    
    motl_final = [motl_exo motl_normal];
    
    
    % Fuse targets:
    target_exo = h5read([path_dset, folder_name, '/target.h5'], '/dataset');
    target(target_exo==1) = 2;
    
    % Make output path if not exist
    if (~exist([output_path, folder_name '/'], 'dir')); mkdir([output_path, folder_name '/']); end%if
    
        % Save data:
    h5create([output_path, folder_name, '/target_wAtlas.h5'], '/dataset', size(target));
    h5write([output_path, folder_name, '/target_wAtlas.h5'], '/dataset', int8(target));
    motl2objlist(motl_final, [output_path, folder_name, '/objl_with_atlas.xml']);
    
end

