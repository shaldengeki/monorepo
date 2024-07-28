const webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin')
const CopyWebpackPlugin = require('copy-webpack-plugin');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

const devMode = process.env.NODE_ENV !== "production";

module.exports = {
  module: {
    rules: [
      {
        test: /\.css$/i,
        use: [
          devMode ? 'style-loader' : MiniCssExtractPlugin.loader,
          'css-loader'
        ],
      },
      {
        test: /\.(png|jpe?g|gif|svg)$/i,
        use: [
          {
            loader: 'file-loader',
          },
        ],
      },
      {
        test: /\.(ico|json)$/,
        exclude: /node_modules/,
        use: [{loader: "file-loader"}]
      },
    ],
  },
  output: {
    publicPath: '/',
  },
  plugins: [
    new CopyWebpackPlugin({
      patterns: [
        {from: 'public/manifest.json', to: ''},
        {from: 'public/robots.txt', to: ''},
      ],
    }),
    new webpack.EnvironmentPlugin({
      "REACT_APP_API_HOST": "api",
      "REACT_APP_API_PORT": "5000",
      "REACT_APP_API_PROTOCOL": "http",
    }),
    new HtmlWebpackPlugin({
      template: "public/index.html",
      favicon: 'public/favicon.ico',
      inject: true,
    }),
    new webpack.ProvidePlugin({
      process: 'process/browser',
    }),
  ],
  resolve: {
    alias: {
      process: "process/browser",
    }
  }
};
