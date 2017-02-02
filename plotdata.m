% Read csv
data = csvread('data.csv');

% Plot
figure;
for index = 1:6
    subplot(2, 3, index);
    plot(data(index, :))
end