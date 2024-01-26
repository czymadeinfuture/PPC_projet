# PPC_projet

hanabi规则：
游戏中有50张烟花牌，分为五种颜色（红、黄、绿、蓝、白），每种颜色有从1到5的不同数值牌。
两种令牌：信息令牌，炸弹令牌
三个堆：抽牌堆，弃牌堆， 中心堆
2-5人
戏的关键特点之一是玩家不能看自己的牌，因此需要依靠其他玩家提供的提示。每个玩家轮流进行动作，包括：给出提示、丢弃一张牌或者打出一张牌。

给出提示：玩家可以选择一种颜色或一个数字，然后指出另一名玩家手中所有对应颜色或数字的牌。给出提示需要消耗一个信息令牌。如果令一位玩家有多种相同颜色或数字的牌，提示者需要全部提示出来。
丢弃牌：玩家可以选择丢弃一张牌，这样做可以恢复一个信息令牌。丢弃的牌将不再参与游戏。
打出牌：玩家尝试打出一张牌来建立或延续烟花。如果牌能正确放置，则游戏继续；如果放置错误，则消耗一个导火索令牌，并将错误的牌放入弃牌堆。

游戏可以以三种方式结束：1.所有炸弹令牌被用完，代表游戏失败；2.成功打出所有5点的烟花牌，获得胜利；3.或者当牌堆中的最后一张牌被抽取后，游戏将在每位玩家再进行一轮后结束。游戏结束时，各色烟花的最高点数牌的总和即为最终得分

在Hanabi游戏中，炸弹令牌代表玩家犯错的机会。当玩家尝试打出一张牌而这张牌不能正确放置时，一个炸弹令牌就会被消耗。具体来说，如果玩家打出的牌不能按正确的数值顺序延续已有的烟花序列，或者尝试开始一个新的烟花序列但没有使用数值为1的牌，那么这张牌就被视为放置错误。
放置错误的牌会被放入弃牌堆，同时翻开一个炸弹令牌，表示犯了一个错误。游戏开始时，所有炸弹令牌都是背面朝上的。当一个错误发生时，玩家需要翻开一个炸弹令牌，显示其正面（通常是闪电标志）。一旦所有炸弹令牌都被翻开，游戏立即结束，玩家们失去比赛。

projet要求规则：