ALTER TABLE `sozin$ladyluck`.`dice_throw_adjustment`
CHANGE COLUMN `adjustment_type` `adjustment_type` ENUM('C', 'R', 'N', 'T') NULL DEFAULT NULL ;


ALTER TABLE `sozin$ladyluck`.`dice`
ADD COLUMN `dice_origination` VARCHAR(8) NULL COMMENT '' AFTER `dice_face`;

update dice
set dice_origination="ROLLED";



