/* Pokémanki
 * Copyright (C) 2023 Exkywor and zjosua
 * Copyright (C) 2024 Shigeyuki
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

Pokemanki = {};

// Dynamically detect addon path from this script's URL
(function () {
  const scripts = document.getElementsByTagName("script");
  const currentScript = scripts[scripts.length - 1];
  const match = currentScript.src.match(/\/_addons\/([^/]+)\//);
  Pokemanki.addonPath = match ? `/_addons/${match[1]}` : "/_addons/576239330";
})();

const popupImageNames = [
  "pipo-popupemotes065.png",
  "pipo-popupemotes066.png",
  "pipo-popupemotes053.png",
  "pipo-popupemotes058.png",
  "pipo-popupemotes059.png",
  "pipo-popupemotes044.png",
  "pipo-popupemotes001.png",
  "pipo-popupemotes002.png",
  "pipo-popupemotes004.png",
  "pipo-popupemotes005.png",
  "pipo-popupemotes007.png",
  "pipo-popupemotes009.png",
  "pipo-popupemotes013.png",
  "pipo-popupemotes014.png",
  "pipo-popupemotes017.png",
  "pipo-popupemotes032.png",
  "pipo-popupemotes050.png",
  "pipo-popupemotes051.png",
  "pipo-popupemotes052.png",
  "pipo-popupemotes060.png",
  "pipo-popupemotes069.png",
  "pipo-popupemotes075.png",
  "pipo-popupemotes076.png",
  "pipo-popupemotes077.png",
  "pipo-popupemotes078.png",
  "pipo-popupemotes080.png",
  "pipo-popupemotes087.png",
  "pipo-popupemotes097.png",
  "pipo-popupemotes064.png",
];
let images = popupImageNames.map(
  (name) => `${Pokemanki.addonPath}/custom_py/pipoya_popup/${name}`
);

Pokemanki.bounce = function bounce(img) {
  let times = Math.floor(Math.random() * 3) + 2; // 2~4のﾗﾝﾀﾞﾑな数を生成
  for (let i = 0; i < times; i++) {
    setTimeout(() => {
      img.style.animation = "none"; // ｱﾆﾒｰｼｮﾝをﾘｾｯﾄ
      // ﾌﾞﾗｳｻﾞがｽﾀｲﾙ変更を認識するための小さな遅延
      setTimeout(() => {
        img.style.animation = "bounce 0.5s";
      }, 10);
    }, i * 500); // 各ﾊﾞｳﾝﾄﾞを0.5秒間隔で実行
  }

  // img要素の親要素の位置を相対位置に設定
  img.parentNode.style.position = "relative";

  // ﾗﾝﾀﾞﾑな画像を表示
  let randomImg = document.createElement("div");
  randomImg.style.position = "absolute";
  randomImg.style.top = img.offsetTop - 32 + "px"; // ｸﾘｯｸした画像の100px上に表示
  randomImg.style.left = img.offsetLeft + img.offsetWidth / 2 - 16 + "px"; // 画像の左右の中央に配置
  randomImg.style.width = "32px"; // 画像の幅を設定
  randomImg.style.height = "32px"; // 画像の高さを設定
  let randomIndex = Math.floor(Math.random() * images.length); // ﾗﾝﾀﾞﾑなｲﾝﾃﾞｯｸｽを計算
  randomImg.style.backgroundImage = `url(${images[randomIndex]})`; // ﾗﾝﾀﾞﾑなｽﾌﾟﾗｲﾄｼｰﾄのURLを設定
  randomImg.style.backgroundPosition = "0px 0px"; // 最初のﾌﾚｰﾑを表示
  img.parentNode.appendChild(randomImg); // img要素の親要素の子要素として追加

  // ｱﾆﾒｰｼｮﾝを開始
  let frame = 0;
  let animationInterval = setInterval(() => {
    frame = (frame + 1) % 3; // 次のﾌﾚｰﾑに移動（3ﾌﾚｰﾑなので､0, 1, 2, 0, 1, 2, ...となる）
    randomImg.style.backgroundPosition = `-${frame * 32}px 0px`; // 次のﾌﾚｰﾑを表示
  }, 500); // 500ﾐﾘ秒ごとにﾌﾚｰﾑを更新

  // 1.5秒後に画像を消す
  setTimeout(() => {
    clearInterval(animationInterval); // ｱﾆﾒｰｼｮﾝを停止
    randomImg.remove(); // 画像を削除
  }, 1500);
};
